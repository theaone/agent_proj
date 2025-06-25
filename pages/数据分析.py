import streamlit as st
import pandas as pd
import openpyxl
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import textwrap
import traceback
import io
import contextlib

# 初始化OpenAI模型
openai_model = ChatOpenAI(
    model='gpt-4o-mini',
    base_url='https://api.openai-hk.com/v1/',
    api_key=SecretStr('hk-cb39871000056422b677a18877f87f49903e49de3b287d70'),
)

# 初始化会话状态
if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.memory = ConversationBufferMemory(return_messages=True)
    st.session_state.df = None
    st.session_state.current_file = None
    st.session_state.waiting_for_sheet = False
    st.session_state.available_sheets = []
    st.session_state.processed_df = None
    st.session_state.last_file_message = None
    st.session_state.initial_message_sent = False  # 标记初始消息是否已发送

# 创建普通聊天链
chain = ConversationChain(llm=openai_model, memory=st.session_state.memory)

# 应用标题
st.title('数据清洗与分析智能助手')

# 发送初始欢迎消息
if not st.session_state.initial_message_sent:
    welcome_msg = "我是数据清洗与分析助手，请上传数据文件并告诉我您的需求"
    st.session_state.history.append({'role': 'ai', 'content': welcome_msg})
    st.session_state.initial_message_sent = True

# 侧边栏 - 文件上传
with st.sidebar:
    st.subheader("上传数据文件")
    uploaded_file = st.file_uploader(
        "选择CSV、Excel或JSON文件",
        type=["csv", "xlsx", "json"],
        key="file_uploader"
    )

    st.divider()
    st.subheader("核心功能")
    st.markdown("""
    - **数据清洗与预处理**:
        - 数据读取与检查
        - 缺失值处理
        - 重复值处理
        - 异常值检测与处理
        - 数据类型转换
        - 数据标准化/归一化
        - 特征工程（新增列）
    - **统计分析**:
        - 描述性统计
        - 相关性分析
        - 数据分布可视化
        - 分组聚合分析
    """)

    # 显示数据摘要（如果已加载）
    if st.session_state.df is not None:
        st.divider()
        st.subheader("数据摘要")
        st.write(f"**文件:** {st.session_state.current_file}")
        st.write(f"**行数:** {st.session_state.df.shape[0]}")
        st.write(f"**列数:** {st.session_state.df.shape[1]}")
        st.write(f"**列名:** {', '.join(st.session_state.df.columns.tolist())}")

        if st.button("清除当前数据", use_container_width=True):
            st.session_state.df = None
            st.session_state.current_file = None
            st.session_state.waiting_for_sheet = False
            st.session_state.history.append({
                'role': 'ai',
                'content': "已清除当前数据集"
            })
            st.rerun()

# 文件上传处理逻辑
if uploaded_file is not None and st.session_state.current_file != uploaded_file.name:
    try:
        # 读取文件
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.session_state.current_file = uploaded_file.name
            st.session_state.waiting_for_sheet = False

            # 创建文件加载消息
            file_message = {
                'role': 'ai',
                'content': f"✅ 已成功加载CSV文件: **{uploaded_file.name}**\n\n"
                           f"数据集包含 **{df.shape[0]}** 行 × **{df.shape[1]}** 列数据\n"
                           f"列名: {', '.join(df.columns.tolist())}"
            }

            # 只有当消息不同时才添加
            if st.session_state.last_file_message != file_message['content']:
                st.session_state.history.append(file_message)
                st.session_state.last_file_message = file_message['content']

                # 显示前5行数据
                preview_msg = {
                    'role': 'ai',
                    'content': "数据预览（前5行）：",
                    'preview': df.head().to_markdown()
                }
                st.session_state.history.append(preview_msg)


        elif uploaded_file.name.endswith('.xlsx'):
            wb = openpyxl.load_workbook(uploaded_file)
            sheets = wb.sheetnames
            st.session_state.available_sheets = sheets

            if len(sheets) > 1:
                # 对于多sheet的Excel，询问用户选择哪个sheet
                st.session_state.waiting_for_sheet = True
                file_message = {
                    'role': 'ai',
                    'content': f"检测到多个工作表：{', '.join(sheets)}\n请告诉我您需要分析哪一个工作表？"
                }
                if st.session_state.last_file_message != file_message['content']:
                    st.session_state.history.append(file_message)
                    st.session_state.last_file_message = file_message['content']
            else:
                # 只有一个工作表，直接加载
                df = pd.read_excel(uploaded_file)
                st.session_state.df = df
                st.session_state.current_file = uploaded_file.name
                st.session_state.waiting_for_sheet = False

                # 创建文件加载消息
                file_message = {
                    'role': 'ai',
                    'content': f"✅ 已成功加载Excel文件: **{uploaded_file.name}**\n"
                               f"工作表: **{sheets[0]}**\n\n"
                               f"数据集包含 **{df.shape[0]}** 行 × **{df.shape[1]}** 列数据\n"
                               f"列名: {', '.join(df.columns.tolist())}"
                }
                if st.session_state.last_file_message != file_message['content']:
                    st.session_state.history.append(file_message)
                    st.session_state.last_file_message = file_message['content']

                    # 显示前5行数据
                    preview_msg = {
                        'role': 'ai',
                        'content': "数据预览（前5行）：",
                        'preview': df.head().to_markdown()
                    }
                    st.session_state.history.append(preview_msg)



        elif uploaded_file.name.endswith('.json'):
            df = pd.read_json(uploaded_file)
            st.session_state.df = df
            st.session_state.current_file = uploaded_file.name
            st.session_state.waiting_for_sheet = False

            # 创建文件加载消息
            file_message = {
                'role': 'ai',
                'content': f"✅ 已成功加载JSON文件: **{uploaded_file.name}**\n\n"
                           f"数据集包含 **{df.shape[0]}** 行 × **{df.shape[1]}** 列数据\n"
                           f"列名: {', '.join(df.columns.tolist())}"
            }
            if st.session_state.last_file_message != file_message['content']:
                st.session_state.history.append(file_message)
                st.session_state.last_file_message = file_message['content']

                # 显示前5行数据
                preview_msg = {
                    'role': 'ai',
                    'content': "数据预览（前5行）：",
                    'preview': df.head().to_markdown()
                }
                st.session_state.history.append(preview_msg)



    except Exception as e:
        error_msg = f"读取文件时出错: {str(e)}"
        if st.session_state.last_file_message != error_msg:
            st.session_state.history.append({
                'role': 'ai',
                'content': error_msg
            })
            st.session_state.last_file_message = error_msg

# 显示聊天对话框
for chat in st.session_state.history:
    with st.chat_message(chat['role']):
        st.write(chat['content'])

        # 显示数据预览（如果有）
        if 'preview' in chat:
            st.markdown(chat['preview'])

        # 显示控制台输出（如果有）
        if 'console_output' in chat and chat['console_output']:
            with st.expander("查看代码执行输出"):
                st.text(chat['console_output'])

        # 显示可视化图表（如果有）
        if 'visualization' in chat:
            st.pyplot(chat['visualization'])
            plt.clf()

        # 显示生成的代码（如果有）
        if 'code' in chat and chat['code']:
            with st.expander("查看生成的Python代码"):
                st.code(chat['code'], language='python')

# 用户输入
user_input = st.chat_input("请输入您的分析需求...")


def safe_execute_code(code, df):
    """安全执行生成的代码，并捕获输出内容"""
    try:
        # 去除代码中所有不必要的缩进
        code = textwrap.dedent(code).strip()

        # 创建安全环境
        local_vars = {'df': df.copy(), 'plt': plt, 'sns': sns, 'np': np, 'pd': pd}
        global_vars = {}

        # 创建一个字符串缓冲区来捕获输出
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            # 添加必要的导入语句
            full_code = f"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

{code}
"""
            # 执行代码
            exec(full_code, global_vars, local_vars)

        # 获取捕获的输出
        console_output = output_buffer.getvalue()

        # 获取处理后的数据
        result_df = local_vars.get('df', df)

        # 获取可视化图表
        if plt.gcf().get_axes():
            fig = plt.gcf()
            return result_df, fig, console_output, None
        return result_df, None, console_output, None
    except Exception as e:
        # 捕获详细的错误信息
        error_trace = traceback.format_exc()
        return df, None, None, f"执行代码时出错:\n{error_trace}"


def extract_code(text):
    """改进的代码提取函数，支持多种格式"""
    if not text:
        return None

    # 尝试提取三重引号内的代码
    triple_quote_pattern = r'\"\"\"(.*?)\"\"\"'
    triple_quote_match = re.search(triple_quote_pattern, text, re.DOTALL)

    if triple_quote_match:
        return triple_quote_match.group(1).strip()

    # 尝试提取Action Input中的代码
    action_input_pattern = r"Action Input:\s*\n?(.*?)(?:\n\n|$)"
    action_input_match = re.search(action_input_pattern, text, re.DOTALL)

    if action_input_match:
        return action_input_match.group(1).strip()

    # 尝试直接提取代码块
    code_block_pattern = r"```python(.*?)```"
    code_block_match = re.search(code_block_pattern, text, re.DOTALL)

    if code_block_match:
        return code_block_match.group(1).strip()

    # 尝试提取没有标记的代码块
    no_marker_pattern = r"```(.*?)```"
    no_marker_match = re.search(no_marker_pattern, text, re.DOTALL)

    return no_marker_match.group(1).strip() if no_marker_match else None


if user_input:
    # 添加用户消息到历史
    st.session_state.history.append({'role': 'human', 'content': user_input})

    # 处理用户请求
    with st.spinner("思考中..."):
        try:
            # 处理工作表选择
            if st.session_state.waiting_for_sheet:
                if user_input in st.session_state.available_sheets:
                    # 读取选定的工作表
                    df = pd.read_excel(uploaded_file, sheet_name=user_input)
                    st.session_state.df = df
                    st.session_state.current_file = uploaded_file.name
                    st.session_state.waiting_for_sheet = False

                    # 添加成功加载消息
                    file_message = {
                        'role': 'ai',
                        'content': f"✅ 已加载工作表: **{user_input}**\n\n"
                                   f"数据集包含 **{df.shape[0]}** 行 × **{df.shape[1]}** 列数据\n"
                                   f"列名: {', '.join(df.columns.tolist())}"
                    }
                    st.session_state.history.append(file_message)
                    st.session_state.last_file_message = file_message['content']

                    # 显示前5行数据
                    preview_msg = {
                        'role': 'ai',
                        'content': "数据预览（前5行）：",
                        'preview': df.head().to_markdown()
                    }
                    st.session_state.history.append(preview_msg)


                else:
                    error_msg = {
                        'role': 'ai',
                        'content': f"未找到工作表: **{user_input}**\n"
                                   f"请从以下工作表中选择: {', '.join(st.session_state.available_sheets)}"
                    }
                    st.session_state.history.append(error_msg)
                    st.session_state.last_file_message = error_msg['content']

            # 如果有数据集，执行数据分析
            elif st.session_state.df is not None:
                # 创建数据分析智能体
                agent = create_pandas_dataframe_agent(
                    llm=openai_model,
                    df=st.session_state.df,
                    verbose=True,
                    max_iterations=5,
                    allow_dangerous_code=True,
                    agent_executor_kwargs={
                        'handle_parsing_errors': True,
                    }
                )

                # 提示词 - 专注于数据清洗与预处理
                prompt = (
                    f"你是一位专业的数据科学家，请根据用户的具体需求执行任务：\n"
                    f"用户需求：{user_input}\n\n"
                    f"请只执行用户明确要求的任务，不要添加额外步骤。\n"
                    f"生成可直接执行的Python代码（使用pandas/seaborn/matplotlib）来解决用户需求。\n"
                    f"注意：数据已经存储在变量`df`中，不需要再次读取。\n"
                    f"确保代码包含所有必要的导入语句。\n"
                    f"使用三重引号包裹完整代码。\n"
                    f"确保代码开头没有不必要的缩进。\n\n"
                    f"输出格式：\n"
                    f"Thought: 你的思考过程\n"
                    f"Action: python_repl_ast\n"
                    f"Action Input: \n\"\"\"\n你的完整Python代码\n\"\"\""
                )

                # 调用智能体
                res = agent.invoke({'input': prompt})
                response_content = res['output']

                # 提取代码
                code = extract_code(response_content)
                processed_df = None
                visualization = None
                console_output = None
                error = None

                if code:
                    # 安全执行代码
                    processed_df, visualization, console_output, error = safe_execute_code(code, st.session_state.df)

                    if error:
                        # 执行出错
                        response_content = error
                    else:
                        # 执行成功
                        st.session_state.processed_df = processed_df

                        # 添加处理成功消息
                        response_content = f"✅ 成功执行代码：{user_input}\n\n"


                else:
                    response_content = "未能在响应中找到可执行的Python代码"

                # 添加AI响应到历史
                ai_response = {
                    'role': 'ai',
                    'content': response_content,
                }

                if code:
                    ai_response['code'] = code

                # 添加控制台输出
                if console_output:
                    ai_response['console_output'] = console_output

                # 添加可视化图表
                if visualization:
                    ai_response['visualization'] = visualization


                st.session_state.history.append(ai_response)

            else:
                # 普通聊天
                res = chain.invoke({'input': user_input})
                response_content = res['response']

                # 添加AI响应到历史
                st.session_state.history.append({'role': 'ai', 'content': response_content})

        except Exception as e:
            error_msg = f"处理请求时出错: {str(e)}"
            st.session_state.history.append({'role': 'ai', 'content': error_msg})

    # 立即重新运行以显示最新消息
    st.rerun()

# 下载处理后的数据
if st.session_state.processed_df is not None:
    st.sidebar.divider()
    st.sidebar.subheader("数据导出")

    csv = st.session_state.processed_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="下载处理后的数据 (CSV)",
        data=csv,
        file_name='processed_data.csv',
        mime='text/csv',
        use_container_width=True
    )