import json
import openpyxl
import pandas as pd
import streamlit as st
import re
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
import plotly.express as px
import plotly.graph_objects as go
import os

# 检查resources目录是否存在，不存在则创建
if not os.path.exists('resources'):
    os.makedirs('resources')
    # 创建示例文件
    with open('project/resources/能力介绍.txt', 'w', encoding='utf-8') as f:
        f.write("数据分析智能体能力介绍：\n1. 数据可视化\n2. 趋势分析\n3. 异常检测\n4. 图形分析")

    with open('project/resources/提示词指南.txt', 'w', encoding='utf-8') as f:
        f.write("提示词使用指南：\n1. 明确指定图表类型\n2. 指定时间范围\n3. 指定关注指标\n4. 可要求分析图形特征")


# 读取文件内容
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
  "answer": "简要文字说明(可选)",
  "analysis": "对生成图形的详细分析(可选)",
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
当前问题："""


def extract_json_from_response(text):
    """终极JSON解析器"""
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


# 模型配置部分保持不变

def dataframe_agent(df, question):
    """稳健版数据分析智能体 - 确保使用完整数据"""
    prompt = PROMPT_PREFIX + question + "\n\n请确保使用完整数据集进行分析，数据长度必须一致，并对生成的图形进行详细分析。"

    agent = create_pandas_dataframe_agent(
        llm=ds_model,
        df=df,
        verbose=True,
        max_iterations=5,
        include_df_in_prompt=True,
        allow_dangerous_code=True,
        agent_executor_kwargs={"return_only_outputs": True}
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
    """增强版结果显示函数 - 支持完整数据展示和图形分析"""
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

    # 显示表格数据
    if 'table' in result:
        try:
            df = pd.DataFrame(
                data=result['table'].get('data', []),
                columns=result['table'].get('columns', [])
            )
            st.dataframe(df)
        except Exception as e:
            st.error(f"表格显示错误: {str(e)}")

    # 展示趋势变化的图表 - 使用完整数据
    if any(chart_type in result for chart_type in ['line', 'area', 'step']):
        col1, col2, col3 = st.columns(3)

        if 'line' in result:
            with col1:
                try:
                    x_data = result['line'].get('columns', [])
                    y_data = result['line'].get('data', [])

                    # 数据长度检查和自动修复
                    if len(x_data) != len(y_data):
                        st.warning(f"折线图数据长度不匹配: x轴({len(x_data)}) y轴({len(y_data)})")
                        if len(y_data) > 0:
                            x_data = list(range(len(y_data)))

                    fig = px.line(
                        x=x_data,
                        y=y_data,
                        title="完整数据折线图"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"折线图生成错误: {str(e)}")

        if 'area' in result:
            with col2:
                try:
                    x_data = result['area'].get('columns', [])
                    y_data = result['area'].get('data', [])

                    if len(x_data) != len(y_data):
                        st.warning(f"面积图数据长度不匹配: x轴({len(x_data)}) y轴({len(y_data)})")
                        if len(y_data) > 0:
                            x_data = list(range(len(y_data)))

                    fig = px.area(
                        x=x_data,
                        y=y_data,
                        title="完整数据面积图"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"面积图生成错误: {str(e)}")

        if 'step' in result:
            with col3:
                try:
                    x_data = result['step'].get('columns', [])
                    y_data = result['step'].get('data', [])

                    if len(x_data) != len(y_data):
                        st.warning(f"阶梯图数据长度不匹配: x轴({len(x_data)}) y轴({len(y_data)})")
                        if len(y_data) > 0:
                            x_data = list(range(len(y_data)))

                    fig = go.Figure(go.Scatter(
                        x=x_data,
                        y=y_data,
                        mode='lines+markers',
                        line_shape='hv',
                        name='完整数据阶梯图'
                    ))
                    fig.update_layout(title="完整数据阶梯图")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"阶梯图生成错误: {str(e)}")

    # 比较数值大小的图表 - 使用完整数据
    if any(chart_type in result for chart_type in ['bar', 'radar', 'waterfall']):
        col1, col2, col3 = st.columns(3)

        if 'bar' in result:
            with col1:
                try:
                    x_data = result['bar'].get('columns', [])
                    y_data = result['bar'].get('data', [])

                    if len(x_data) != len(y_data):
                        st.warning(f"柱状图数据长度不匹配: x轴({len(x_data)}) y轴({len(y_data)})")
                        if len(y_data) > 0:
                            x_data = list(range(len(y_data)))

                    fig = px.bar(
                        x=x_data,
                        y=y_data,
                        title="完整数据柱状图"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"柱状图生成错误: {str(e)}")

        if 'radar' in result:
            with col2:
                try:
                    fig = go.Figure(go.Scatterpolar(
                        r=result['radar'].get('r', []),
                        theta=result['radar'].get('theta', []),
                        fill='toself',
                        name='完整数据雷达图'
                    ))
                    fig.update_layout(title="完整数据雷达图")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"雷达图生成错误: {str(e)}")

        if 'waterfall' in result:
            with col3:
                try:
                    fig = go.Figure(go.Waterfall(
                        x=result['waterfall'].get('x', []),
                        y=result['waterfall'].get('y', []),
                        textposition="outside",
                        connector={"line": {"color": "rgb(63, 63, 63)"}},
                    ))
                    fig.update_layout(title="完整数据瀑布图")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"瀑布图生成错误: {str(e)}")

    # 显示占比关系的图表 - 使用完整数据
    if any(chart_type in result for chart_type in ['pie', 'donut']):
        col1, col2 = st.columns(2)

        if 'pie' in result:
            with col1:
                try:
                    fig = px.pie(
                        names=result['pie'].get('labels', []),
                        values=result['pie'].get('values', []),
                        title="完整数据饼图"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"饼图生成错误: {str(e)}")

        if 'donut' in result:
            with col2:
                try:
                    fig = px.pie(
                        names=result['donut'].get('labels', []),
                        values=result['donut'].get('values', []),
                        hole=0.4,
                        title="完整数据环形图"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"环形图生成错误: {str(e)}")

    # 展示分布情况的图表 - 使用完整数据
    if any(chart_type in result for chart_type in ['scatter', 'heatmap', 'histogram']):
        col1, col2, col3 = st.columns(3)

        if 'scatter' in result:
            with col1:
                try:
                    fig = px.scatter(
                        x=result['scatter'].get('x', []),
                        y=result['scatter'].get('y', []),
                        size=result['scatter'].get('size', []),
                        title="完整数据散点图"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"散点图生成错误: {str(e)}")

        if 'heatmap' in result:
            with col2:
                try:
                    fig = go.Figure(go.Heatmap(
                        x=result['heatmap'].get('x', []),
                        y=result['heatmap'].get('y', []),
                        z=result['heatmap'].get('z', []),
                        colorscale='Viridis'
                    ))
                    fig.update_layout(title="完整数据热力图")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"热力图生成错误: {str(e)}")

        if 'histogram' in result:
            with col3:
                try:
                    fig = px.histogram(
                        x=result['histogram'].get('values', []),
                        title="完整数据直方图"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"直方图生成错误: {str(e)}")

    # 展示关系网络的图表 - 使用完整数据
    if any(chart_type in result for chart_type in ['network', 'tree', 'sankey']):

        if 'tree' in result:
            try:
                fig = go.Figure(go.Treemap(
                    labels=result['tree'].get('labels', []),
                    parents=result['tree'].get('parents', []),
                    marker_colors=["#636EFA", "#EF553B", "#00CC96"]
                ))
                fig.update_layout(title="完整数据树形图")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"树形图生成错误: {str(e)}")

        if 'sankey' in result:
            try:
                fig = go.Figure(go.Sankey(
                    node=dict(
                        label=result['sankey'].get('nodes', [])
                    ),
                    link=dict(
                        source=[link.get('source') for link in result['sankey'].get('links', [])],
                        target=[link.get('target') for link in result['sankey'].get('links', [])],
                        value=[link.get('value') for link in result['sankey'].get('links', [])]
                    )
                ))
                fig.update_layout(title="完整数据桑基图")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"桑基图生成错误: {str(e)}")


def show_sidebar_content(title, filename):
    """显示侧边栏内容"""
    content = read_file_content(filename)
    with st.sidebar:
        st.header(title)
        st.markdown("---")
        st.markdown(content)


# 初始化会话状态
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'raw_response' not in st.session_state:
    st.session_state['raw_response'] = ''
if 'conversation_pairs' not in st.session_state:
    st.session_state['conversation_pairs'] = []  # 存储完整的问答对
if 'selected_conversation' not in st.session_state:
    st.session_state['selected_conversation'] = None  # 当前选中的对话索引
if 'active_sidebar' not in st.session_state:
    st.session_state['active_sidebar'] = None  # 当前激活的侧边栏

# 设置页面配置
st.set_page_config(page_title="数据分析智能体", layout="wide")

# 主界面
st.title("📊 数据分析智能体")

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
            st.dataframe(st.session_state['df'].head(3))
        except Exception as e:
            st.error(f"文件加载失败: {str(e)}")

# 显示所有对话内容
for i, pair in enumerate(st.session_state['conversation_pairs']):
    # 高亮显示选中的对话
    if i == st.session_state['selected_conversation']:
        st.markdown("---")
        st.markdown("**当前查看的对话:**")

    with st.chat_message("user"):
        st.write(pair['question'])
    with st.chat_message("assistant"):
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

    with st.spinner('分析中...'):
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
    st.error("请先上传数据文件")

# 历史对话侧边栏
with st.sidebar:
    st.header("🗒️ 对话历史")

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

    # 显示当前选中的对话详情
    if st.session_state['selected_conversation'] is not None:
        st.markdown("---")
        pair = st.session_state['conversation_pairs'][st.session_state['selected_conversation']]

