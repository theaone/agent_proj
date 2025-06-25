import json
import openpyxl
import pandas as pd
import streamlit as st
import re
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
import plotly.express as px#高级可视化库
import plotly.graph_objects as go
import os
from datetime import datetime

def read_file_content(filename):
    try:
        with open(f'resources/{filename}', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"文件 {filename} 未找到"

# 模型配置
ds_model = ChatOpenAI(
    model='deepseek-chat',
    base_url='https://api.deepseek.com/v1',
    api_key=SecretStr('sk-6a9e3dcc6eed4711957608bd24fdc6b4'),
)

# 增强版提示词模板 - 强调使用完整数据
PROMPT_PREFIX = """你是一位数据分析助手，请严格按照以下JSON格式返回结果，并确保使用完整数据集进行分析：
{
  "answer": "简要文字说明",
  "analysis": "对生成图形的详细分析",
  "table": {
    "columns": ["列名1", "列名2"],
    "data": [[值1, 值2], [值3, 值4]]
  },
  "bar": {
    "columns": ["A", "B"],  # 必须与data长度相同
    "data": [10, 20]       # 必须与columns长度相同
  },
  "line": {
    "columns": ["A", "B"],  # 必须与data长度相同的x轴标签
    "data": [10, 20]        # 必须与columns长度相同
  },
  "area": {
    "columns": ["A", "B"],  # 必须与data长度相同
    "data": [10, 20]        # 必须与columns长度相同
  },
  "step": {
    "columns": ["A", "B"],  # 必须与data长度相同
    "data": [10, 20]        # 必须与columns长度相同
  },
  "pie": {
    "labels": ["A", "B"],
    "values": [10, 20]
  },
  "donut": {
    "labels": ["A", "B"],
    "values": [10, 20]
  },
  "scatter": {
    "x": [1, 2],
    "y": [10, 20],
    "size": [5, 10]
  },
  "heatmap": {
    "x": ["A", "B"],
    "y": ["X", "Y"],
    "z": [[1, 2], [3, 4]]
  },
  "histogram": {
    "values": [1, 2, 2, 3, 3, 3]
  },
  "radar": {
    "r": [1, 2, 3],
    "theta": ["A", "B", "C"]
  },
  "waterfall": {
    "x": ["A", "B", "C"],
    "y": [10, -5, 5]
  },
  "network": {
    "nodes": [
      {"id": 1, "label": "Node 1", "size": 10},
      {"id": 2, "label": "Node 2", "size": 5}
    ],
    "edges": [
      {"from": 1, "to": 2, "value": 5}
    ]
  },
  "tree": {
    "labels": ["Parent", "Child1", "Child2"],
    "parents": ["", "Parent", "Parent"]
  },
  "sankey": {
    "nodes": ["A", "B", "C"],
    "links": [
      {"source": 0, "target": 1, "value": 10},
      {"source": 1, "target": 2, "value": 5}
    ]
  }
}
注意：1. 所有字符串用双引号 2. 数值不加引号 3. 图表数据必须保持长度一致 4. 只返回JSON，不要额外文本
在提示词中明确要求只返回请求的图表类型

在解析响应时识别用户请求的图表类型

只绘制用户请求的图表
当前问题："""


def extract_json_from_response(text):
    """终极JSON解析器 从响应文本中提取JSON数据"""
    try:
        # 尝试直接提取最外层JSON
        text = text.replace("'", '"').strip()
        json_str = re.search(r'\{.*\}', text, re.DOTALL)
        if json_str:
            result = json.loads(json_str.group(0))

            # 数据长度验证和自动修复
            for chart_type in ['line', 'bar', 'area', 'step']:
                if chart_type in result:
                    cols = result[chart_type].get('columns', [])
                    data = result[chart_type].get('data', [])
                    if len(cols) != len(data):
                        if len(data) > 0:
                            result[chart_type]['columns'] = list(range(len(data)))
                        else:
                            result[chart_type]['columns'] = []

            return result

        # 尝试从错误消息中提取
        error_json = re.search(r'LLM output:\s*(\{.*?\})', text, re.DOTALL)
        if error_json:
            return json.loads(error_json.group(1))

        # 尝试手动构建
        if "columns" in text and "data" in text:
            columns = re.search(r'columns":\s*\[(.*?)\]', text).group(1)
            data = re.search(r'data":\s*\[(.*?)\]', text).group(1)
            return {
                "bar": {
                    "columns": [x.strip(' "\'') for x in columns.split(',')],
                    "data": [int(x.strip()) for x in data.split(',')]
                }
            }

        return {"answer": text}
    except Exception as e:
        return {"answer": f"解析错误: {str(e)}", "raw": text}

def generate_chart_title(chart_type, question):
    """自动生成图表标题和轴标签"""
    # 从问题中提取关键信息
    keywords = re.findall(r'[A-Za-z0-9]+', question)
    main_keywords = [kw for kw in keywords if len(kw) > 3][:2]

    # 根据图表类型生成标题
    chart_names = {
        'line': '趋势图',
        'bar': '柱状图',
        'pie': '饼图',
        'scatter': '散点图',
        'heatmap': '热力图',
        'histogram': '分布图',
        'area': '面积图',
        'donut': '环形图',
        'radar': '雷达图',
        'waterfall': '瀑布图',
        'tree': '树形图',
        'sankey': '桑基图'
    }

    chart_name = chart_names.get(chart_type, '图表')
    title = f"{' '.join(main_keywords)} {chart_name}" if main_keywords else f"数据{chart_name}"

    # 生成轴标签
    x_label = f"{main_keywords[0]} (单位)" if main_keywords else "X轴"
    y_label = f"{main_keywords[-1]} (单位)" if main_keywords else "Y轴"

    return title, x_label, y_label

def apply_chart_style(fig, chart_type):
    """应用统一的图表样式和颜色方案
    参数:
        fig (plotly.graph_objects.Figure): 图表对象
        chart_type (str): 图表类型

    返回:
        plotly.graph_objects.Figure: 应用样式后的图表对象
    """

    # 设置统一的字体和背景
    fig.update_layout(
        font_family="Arial",
        plot_bgcolor='rgba(240,240,240,1)',
        paper_bgcolor='rgba(255,255,255,1)',
        margin=dict(l=20, r=20, t=40, b=20)
    )

    # 根据图表类型应用特定样式
    if chart_type in ['line', 'area', 'step']:
        fig.update_traces(line=dict(width=2.5))
    elif chart_type == 'bar':
        fig.update_traces(marker_line_width=0.5, marker_line_color='white')
    elif chart_type in ['pie', 'donut']:
        fig.update_traces(textposition='inside', textinfo='percent+label')
    elif chart_type == 'scatter':
        fig.update_traces(marker=dict(size=12, opacity=0.7))
    elif chart_type == 'heatmap':
        fig.update_traces(showscale=True, colorscale='Viridis')

    # 应用响应式设计
    fig.update_layout(
        autosize=True,
        hovermode='closest'
    )

    return fig

def optimize_data_display(data, chart_type):
    """优化数据展示效果

    参数:
        data (list): 原始数据列表
        chart_type (str): 图表类型

    返回:
        list: 优化后的数据列表
    """
    if not data:
        return data

    # 对于时间序列数据，尝试转换日期格式
    if chart_type in ['line', 'area', 'step', 'bar']:
        try:
            if isinstance(data[0], str) and any(d.isdigit() for d in data):
                # 尝试解析日期
                parsed_dates = [pd.to_datetime(d, errors='ignore') for d in data]
                if all(isinstance(d, pd.Timestamp) for d in parsed_dates):
                    # 如果是日期，格式化为更友好的形式
                    return [d.strftime('%Y-%m-%d') if not pd.isna(d) else d for d in parsed_dates]
        except:
            pass

    # 对于数值数据，限制小数位数
    if isinstance(data[0], (int, float)):
        return [round(float(d), 2) if d is not None else 0 for d in data]

    return data

def dataframe_agent(df, question):
    """稳健版数据分析智能体 - 确保使用完整数据"""
    prompt = PROMPT_PREFIX + question + "\n\n请确保使用完整数据集进行分析，数据长度必须一致，并对生成的图形进行详细分析。"

    agent = create_pandas_dataframe_agent(
        llm=ds_model,
        df=df,
        verbose=True,# 详细输出
        max_iterations=5,# 最大迭代次数
        include_df_in_prompt=True, # 在提示中包含数据框
        allow_dangerous_code=True,# 允许执行代码
        agent_executor_kwargs={"return_only_outputs": True}# 只返回输出
    )

    try:
        response = agent.invoke({"input": prompt})
        output = response.get("output", str(response))
        st.session_state['raw_response'] = output
        return extract_json_from_response(output)
    except Exception as e:
        error_response = extract_json_from_response(str(e))
        return error_response if isinstance(error_response, dict) else {"answer": str(e)}

def numerical_analysis_agent(df, question):
    """直接数值分析引擎 - 不生成可视化，只返回计算结果"""
    numerical_prompt = f"""你是一个数值计算引擎，请直接回答数值问题，不需要解释过程。
    当前数据集列名：{', '.join(df.columns)}。
    请严格按照以下格式返回结果：
    {{
      "answer": "直接数值答案",
      "calculation": "使用的计算公式(可选)",
      "metrics": {{
        "min": 最小值,
        "max": 最大值,
        "mean": 平均值,
        "median": 中位数,
        "std": 标准差
      }}
    }}
    问题：{question}"""

    try:
        agent = create_pandas_dataframe_agent(
            llm=ds_model,
            df=df,
            verbose=False,
            allow_dangerous_code=True,
            max_iterations=3,
        )

        response = agent.invoke({"input": numerical_prompt})
        output = response.get("output", str(response))

        if isinstance(output, dict):
            return output
        elif '{' in output and '}' in output:
            try:
                return json.loads(output[output.index('{'):output.rindex('}') + 1])
            except json.JSONDecodeError:
                return {"answer": output}
        return {"answer": output}
    except Exception as e:
        return {"answer": f"计算错误: {str(e)}", "details": str(e)}


def display_result(result):
    """增强版结果显示函数 - 专注于图形展示"""
    if not isinstance(result, dict):
        try:
            result = json.loads(result)
        except:
            result = {"answer": str(result)}

    # 显示基本回答
    if 'answer' in result:
        st.write(result['answer'])

    # 显示图形分析
    if 'analysis' in result:
        st.subheader("📊 图形分析")
        st.write(result['analysis'])

    # 显示趋势变化的图表 - 使用完整数据并调整大小
    if any(chart_type in result for chart_type in ['line', 'area', 'step']):
        for chart_type in ['line', 'area', 'step']:
            if chart_type in result:
                try:
                    x_data = optimize_data_display(result[chart_type].get('columns', []), chart_type)
                    y_data = optimize_data_display(result[chart_type].get('data', []), chart_type)

                    # 数据长度检查和自动修复
                    if len(x_data) != len(y_data):
                        if len(y_data) > 0:
                            x_data = list(range(len(y_data)))

                    title, x_label, y_label = generate_chart_title(chart_type, result.get('answer', ''))

                    if chart_type == 'line':
                        fig = px.line(
                            x=x_data,
                            y=y_data,
                            title=title,
                            labels={'x': x_label, 'y': y_label}
                        )
                    elif chart_type == 'area':
                        fig = px.area(
                            x=x_data,
                            y=y_data,
                            title=title,
                            labels={'x': x_label, 'y': y_label}
                        )
                    else:  # step
                        fig = go.Figure(go.Scatter(
                            x=x_data,
                            y=y_data,
                            mode='lines+markers',
                            line_shape='hv',
                            name=title
                        ))
                        fig.update_layout(
                            title=title,
                            xaxis_title=x_label,
                            yaxis_title=y_label
                        )

                    fig.update_layout(
                        height=500,  # 增加图表高度
                        margin=dict(l=20, r=20, t=60, b=20),
                        autosize=True
                    )
                    fig = apply_chart_style(fig, chart_type)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"{chart_type}图生成错误: {str(e)}")

    # 显示比较数值大小的图表
    if any(chart_type in result for chart_type in ['bar', 'radar', 'waterfall']):
        for chart_type in ['bar', 'radar', 'waterfall']:
            if chart_type in result:
                try:
                    if chart_type == 'bar':
                        x_data = optimize_data_display(result['bar'].get('columns', []), 'bar')
                        y_data = optimize_data_display(result['bar'].get('data', []), 'bar')

                        if len(x_data) != len(y_data):
                            if len(y_data) > 0:
                                x_data = list(range(len(y_data)))

                        title, x_label, y_label = generate_chart_title('bar', result.get('answer', ''))

                        fig = px.bar(
                            x=x_data,
                            y=y_data,
                            title=title,
                            labels={'x': x_label, 'y': y_label},
                            color=x_data,
                            color_continuous_scale='Bluered'
                        )
                    elif chart_type == 'radar':
                        title, _, _ = generate_chart_title('radar', result.get('answer', ''))

                        fig = go.Figure(go.Scatterpolar(
                            r=optimize_data_display(result['radar'].get('r', []), 'radar'),
                            theta=optimize_data_display(result['radar'].get('theta', []), 'radar'),
                            fill='toself',
                            name=title
                        ))
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(visible=True),
                                angularaxis=dict(direction="clockwise")
                            )
                        )
                    else:  # waterfall
                        x_data = optimize_data_display(result['waterfall'].get('x', []), 'waterfall')
                        y_data = optimize_data_display(result['waterfall'].get('y', []), 'waterfall')

                        title, x_label, y_label = generate_chart_title('waterfall', result.get('answer', ''))

                        fig = go.Figure(go.Waterfall(
                            x=x_data,
                            y=y_data,
                            textposition="outside",
                            connector={"line": {"color": "rgb(63, 63, 63)"}},
                            name=title
                        ))
                        fig.update_layout(
                            xaxis_title=x_label,
                            yaxis_title=y_label
                        )

                    fig.update_layout(
                        height=500,
                        margin=dict(l=20, r=20, t=60, b=20),
                        autosize=True
                    )
                    fig = apply_chart_style(fig, chart_type)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"{chart_type}图生成错误: {str(e)}")

    # 显示占比关系的图表
    if any(chart_type in result for chart_type in ['pie', 'donut']):
        for chart_type in ['pie', 'donut']:
            if chart_type in result:
                try:
                    labels = optimize_data_display(result[chart_type].get('labels', []), chart_type)
                    values = optimize_data_display(result[chart_type].get('values', []), chart_type)

                    title, _, _ = generate_chart_title(chart_type, result.get('answer', ''))

                    fig = px.pie(
                        names=labels,
                        values=values,
                        title=title,
                        hole=0.4 if chart_type == 'donut' else 0,
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    fig.update_layout(
                        height=500,
                        margin=dict(l=20, r=20, t=60, b=20),
                        autosize=True
                    )
                    fig = apply_chart_style(fig, chart_type)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"{chart_type}图生成错误: {str(e)}")

    # 显示分布情况的图表
    if any(chart_type in result for chart_type in ['scatter', 'heatmap', 'histogram']):
        for chart_type in ['scatter', 'heatmap', 'histogram']:
            if chart_type in result:
                try:
                    if chart_type == 'scatter':
                        x_data = optimize_data_display(result['scatter'].get('x', []), 'scatter')
                        y_data = optimize_data_display(result['scatter'].get('y', []), 'scatter')
                        size_data = optimize_data_display(result['scatter'].get('size', []), 'scatter') or [10] * len(x_data)

                        title, x_label, y_label = generate_chart_title('scatter', result.get('answer', ''))

                        fig = px.scatter(
                            x=x_data,
                            y=y_data,
                            size=size_data,
                            title=title,
                            labels={'x': x_label, 'y': y_label},
                            color=y_data,
                            color_continuous_scale='Rainbow'
                        )
                    elif chart_type == 'heatmap':
                        x_data = optimize_data_display(result['heatmap'].get('x', []), 'heatmap')
                        y_data = optimize_data_display(result['heatmap'].get('y', []), 'heatmap')
                        z_data = optimize_data_display(result['heatmap'].get('z', []), 'heatmap')

                        title, x_label, y_label = generate_chart_title('heatmap', result.get('answer', ''))

                        fig = go.Figure(go.Heatmap(
                            x=x_data,
                            y=y_data,
                            z=z_data,
                            colorscale='Viridis',
                            name=title
                        ))
                        fig.update_layout(
                            xaxis_title=x_label,
                            yaxis_title=y_label
                        )
                    else:  # histogram
                        values = optimize_data_display(result['histogram'].get('values', []), 'histogram')

                        title, x_label, y_label = generate_chart_title('histogram', result.get('answer', ''))

                        fig = px.histogram(
                            x=values,
                            title=title,
                            labels={'x': x_label, 'y': y_label},
                            nbins=min(20, len(set(values))),
                            color_discrete_sequence=['#636EFA']
                        )

                    fig.update_layout(
                        height=500,
                        margin=dict(l=20, r=20, t=60, b=20),
                        autosize=True
                    )
                    fig = apply_chart_style(fig, chart_type)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"{chart_type}图生成错误: {str(e)}")

    # 显示关系网络的图表
    if any(chart_type in result for chart_type in ['tree', 'sankey']):
        for chart_type in ['tree', 'sankey']:
            if chart_type in result:
                try:
                    if chart_type == 'tree':
                        labels = optimize_data_display(result['tree'].get('labels', []), 'tree')
                        parents = optimize_data_display(result['tree'].get('parents', []), 'tree')

                        title, _, _ = generate_chart_title('tree', result.get('answer', ''))

                        fig = go.Figure(go.Treemap(
                            labels=labels,
                            parents=parents,
                            marker_colors=["#636EFA", "#EF553B", "#00CC96"],
                            name=title
                        ))
                    else:  # sankey
                        nodes = optimize_data_display(result['sankey'].get('nodes', []), 'sankey')
                        links = result['sankey'].get('links', [])

                        title, _, _ = generate_chart_title('sankey', result.get('answer', ''))

                        fig = go.Figure(go.Sankey(
                            node=dict(
                                label=nodes,
                                color=['#636EFA' for _ in nodes]
                            ),
                            link=dict(
                                source=[link.get('source') for link in links],
                                target=[link.get('target') for link in links],
                                value=[link.get('value') for link in links],
                                color=['rgba(99, 110, 250, 0.3)' for _ in links]
                            )
                        ))

                    fig.update_layout(
                        height=600,  # 网络图需要更大高度
                        margin=dict(l=20, r=20, t=60, b=20),
                        autosize=True
                    )
                    fig = apply_chart_style(fig, chart_type)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"{chart_type}图生成错误: {str(e)}")
def show_sidebar_content(title, filename):
    """显示侧边栏内容"""
    content = read_file_content(filename)
    with st.sidebar:
        st.header(title)
        st.markdown("---")
        st.markdown(content)


# 初始化会话状态
if 'history' not in st.session_state:
    st.session_state['history'] = []# 存储对话历史
if 'df' not in st.session_state:
    st.session_state['df'] = None# 存储当前数据框
if 'raw_response' not in st.session_state:
    st.session_state['raw_response'] = ''# 存储原始响应
if 'conversation_pairs' not in st.session_state:
    st.session_state['conversation_pairs'] = []  # 存储完整的问答对
if 'selected_conversation' not in st.session_state:
    st.session_state['selected_conversation'] = None  # 当前选中的对话索引
if 'active_sidebar' not in st.session_state:
    st.session_state['active_sidebar'] = None  # 当前激活的侧边栏

# 设置页面配置
st.set_page_config(page_title="数据分析可视化", layout="wide")

# 主界面
st.title("📊 数据分析可视化")

# 图片展示区域 - 使用Streamlit原生组件
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 能力介绍", use_container_width=True):
        st.session_state['active_sidebar'] = 'capability'  # 设置当前激活的侧边栏

with col2:
    if st.button("💡 提示词指南", use_container_width=True):
        st.session_state['active_sidebar'] = 'prompt'  # 设置当前激活的侧边栏

# 根据激活状态显示侧边栏内容
if st.session_state.get('active_sidebar') == 'capability':
    show_sidebar_content("能力介绍", "能力介绍.txt")
elif st.session_state.get('active_sidebar') == 'prompt':
    show_sidebar_content("提示词指南", "提示词指南.txt")

# 文件上传区域
with st.expander("📤 上传数据文件", expanded=True):
    file_type = st.radio('文件类型:', ['Excel', 'CSV'], horizontal=True)
    file = st.file_uploader('选择文件:', type=['xlsx' if file_type == 'Excel' else 'csv'])

    if file:
        try:
            if file_type == 'Excel':
                wb = openpyxl.load_workbook(file)
                sheet = st.selectbox('选择工作表:', wb.sheetnames)
                st.session_state['df'] = pd.read_excel(file, sheet_name=sheet)
            else:
                st.session_state['df'] = pd.read_csv(file)
            st.success("数据加载成功！")
            st.dataframe(st.session_state['df'].head(3).style.format(precision=2))
        except Exception as e:
            st.error(f"文件加载失败: {str(e)}")

# 显示所有对话内容
for i, pair in enumerate(st.session_state['conversation_pairs']):
    # 高亮显示选中的对话
    if i == st.session_state['selected_conversation']:
        st.markdown("---")
        st.markdown("**当前查看的对话:**")

    with st.chat_message("user"):# 用户消息样式
        st.write(pair['question'])
    with st.chat_message("assistant"): # 助手消息样式
        display_result(json.loads(pair['answer']))

    if i == st.session_state['selected_conversation']:
        st.markdown("---")

# 问题输入区域
question = st.chat_input("请输入分析问题")

if question and st.session_state.get('df') is not None:
    # 显示用户问题
    with st.chat_message("user"):
        st.write(question)

    # 添加到历史记录
    st.session_state['history'].append({'role': 'human', 'content': question})

    with st.spinner('分析中...'):# 加载动画
        # 判断是否应该使用数值分析
        numerical_keywords = ['计算', '多少', '平均值', '总和', '差异', '比率', '占比']
        if any(keyword in question for keyword in numerical_keywords):
            result = numerical_analysis_agent(st.session_state['df'], question)
        else:
            result = dataframe_agent(st.session_state['df'], question)

    # 将结果转换为可序列化的JSON字符串
    try:
        result_str = json.dumps(result)
    except:
        result_str = str(result)

    # 添加到历史记录
    st.session_state['history'].append({'role': 'ai', 'content': result_str})

    # 保存完整的问答对
    st.session_state['conversation_pairs'].append({
        'question': question,
        'answer': result_str
    })

    # 自动选中最新对话
    st.session_state['selected_conversation'] = len(st.session_state['conversation_pairs']) - 1

    # 显示AI回答
    with st.chat_message("assistant"):
        display_result(result)

    # 强制重新渲染页面以保持所有对话可见
    st.rerun()

elif question and not st.session_state.get('df'):
    st.error("请先上传数据文件")# 错误提示
# 侧边栏 - 对话历史
with st.sidebar:
    st.header("🗒️ 对话历史") # 侧边栏标题

    # 添加"查看全部"按钮
    if st.button("查看全部对话"):
        st.session_state['selected_conversation'] = None
        st.rerun()

    # 显示对话列表
    for i, pair in enumerate(st.session_state['conversation_pairs']):
        btn_label = f"对话 {i + 1}: {pair['question'][:20]}..." if len(
            pair['question']) > 20 else f"对话 {i + 1}: {pair['question']}"

        if st.button(btn_label, key=f"conv_btn_{i}"):
            st.session_state['selected_conversation'] = i
            st.rerun()

    # 状态变化检测
    if 'last_selected' not in st.session_state:
        st.session_state['last_selected'] = None

    if st.session_state['last_selected'] != st.session_state['selected_conversation']:
        st.session_state['last_selected'] = st.session_state['selected_conversation']
        st.rerun()

    # 显示当前选中的对话详情
    if st.session_state['selected_conversation'] is not None:
        st.markdown("---")
        pair = st.session_state['conversation_pairs'][st.session_state['selected_conversation']]
        st.text_area("问题", pair['question'], height=100, key=f"q_{st.session_state['selected_conversation']}")
        st.text_area("回答", pair['answer'], height=200, key=f"a_{st.session_state['selected_conversation']}")