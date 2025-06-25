import streamlit as st
import requests
import chardet
import pandas as pd
import io
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from pydantic import SecretStr
from langchain.schema import HumanMessage, AIMessage

# 页面配置
st.set_page_config(
    page_title="问答小助手",
    page_icon="💬",
    layout="wide"
)

# 初始化会话状态
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_summary" not in st.session_state:
    st.session_state.file_summary = ""

if "file_content" not in st.session_state:
    st.session_state.file_content = ""


# 主函数
def main():
    st.title("问答小助手 💬")
    st.markdown("上传文件进行内容概括，或直接向我提问！")

    # 侧边栏配置
    with st.sidebar.expander("🔧 模型配置", expanded=True):
        api_base = st.text_input(
            "API 地址",
            value="https://open.bigmodel.cn/api/paas/v4",
            placeholder="输入大模型API地址"
        )
        api_key = st.text_input(
            "API 密钥",
            value="de909b44bdec44e5a58be445c417f957.izd6sARYwJrNCDAM",
            type="password",
            placeholder="输入你的API密钥"
        )
        model_name = st.selectbox(
            "模型选择",
            ["glm-4-air", "glm-4", "chatglm-pro"]
        )
        temperature = st.slider(
            "生成温度",
            min_value=0.0, max_value=1.0, value=0.1,
            help="控制输出的随机性，较低值更确定性"
        )

        # 记忆功能设置
        st.subheader("💾 对话记忆")
        use_memory = st.checkbox("启用对话记忆", value=True)
        if use_memory:
            if st.button("🧹 清空对话历史"):
                st.session_state.memory.clear()
                st.session_state.messages = []
                st.success("对话历史已清空")

        # 调试选项
        st.subheader("🔧 调试选项")
        st.session_state.debug_mode = st.checkbox("启用调试模式", False)
        if st.session_state.debug_mode:
            st.warning("调试模式会显示详细的 API 响应信息，可能包含敏感数据")

    # 文件上传区域
    with st.expander("📁 上传文件进行内容概括", expanded=True):
        uploaded_file = st.file_uploader(
            "支持 .txt, .md, .csv, .xlsx",
            type=["txt", "md", "csv", "xlsx"]
        )

        if uploaded_file:
            file_extension = uploaded_file.name.split(".")[-1].lower()
            raw_data = uploaded_file.read()

            # 检测编码
            detect_result = chardet.detect(raw_data)
            encoding = detect_result.get('encoding', 'utf-8')

            try:
                # 提取文本内容
                if file_extension in ["txt", "md"]:
                    text_content = raw_data.decode(encoding)
                elif file_extension == "csv":
                    decoded_data = raw_data.decode(encoding)
                    df = pd.read_csv(io.StringIO(decoded_data))
                    text_content = "\n".join([
                        f"{row['姓名']} 的年龄是 {row['年龄']}"
                        for _, row in df.iterrows()
                    ]) if '姓名' in df.columns and '年龄' in df.columns else str(df.to_csv(sep="\t"))
                elif file_extension == "xlsx":
                    df = pd.read_excel(io.BytesIO(raw_data))
                    text_content = "\n".join([
                        f"{row['学科']} 的成绩是 {row['成绩']}"
                        for _, row in df.iterrows()
                    ]) if '学科' in df.columns and '成绩' in df.columns else str(df.to_csv(sep="\t"))

                # 显示文件预览
                with st.expander("📖 文件内容预览", expanded=False):
                    st.text_area("", text_content[:1000] + ("..." if len(text_content) > 1000 else ""), height=150)

                # 保存文件内容到会话状态
                st.session_state.file_content = text_content

                # 选择概括级别
                summary_level = st.selectbox(
                    "概括级别",
                    ["简要概述", "详细摘要", "关键要点"]
                )

                # 概括文章内容
                if st.button("📝 生成内容概括"):
                    with st.spinner("正在分析并概括文章内容..."):
                        # 根据选择的概括级别构建提示词
                        if summary_level == "简要概述":
                            prompt = f"请为以下内容生成一个简明扼要的概述（不超过300字）：\n{text_content[:4000]}"
                        elif summary_level == "详细摘要":
                            prompt = f"请为以下内容生成一个详细的摘要（保留关键信息和主要论点）：\n{text_content[:4000]}"
                        else:  # 关键要点
                            prompt = f"请提取以下内容的关键要点（用列表形式呈现）：\n{text_content[:4000]}"

                        # 调用模型生成概括
                        payload = {
                            "model": model_name,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": temperature
                        }
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}"
                        }

                        try:
                            response = requests.post(
                                f"{api_base}/chat/completions",
                                headers=headers,
                                json=payload,
                                timeout=60
                            ).json()

                            # 提取概括内容
                            if "choices" in response and len(response["choices"]) > 0:
                                summary = response["choices"][0]["message"]["content"].strip()
                                st.session_state.file_summary = summary

                                # 显示概括结果
                                st.subheader("📄 内容概括结果")
                                st.markdown(summary)
                                st.success("内容概括完成！可以基于此内容继续提问")
                            else:
                                st.error(f"无法解析响应格式: {response}")

                        except Exception as e:
                            st.error(f"生成概括失败: {str(e)}")

            except UnicodeDecodeError:
                st.error(f"无法解码文件，可能是编码问题（检测到编码: {encoding}）")

    # 用户输入区域
    st.subheader("❓ 向我提问")
    user_query = st.text_area(
        "",
        placeholder="输入问题，按提交按钮发送...",
        height=100
    )

    # 基于概括内容的快捷提问
    if st.session_state.file_summary:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("概括的主要观点是什么？"):
                user_query = "概括的主要观点是什么？"
        with col2:
            if st.button("请详细解释某个要点"):
                user_query = "请详细解释某个要点"

    if st.button("🚀 提交问题", type="primary"):
        if not user_query.strip():
            st.warning("请输入问题内容")
            return

        # 添加用户问题到对话历史
        st.session_state.messages.append(HumanMessage(content=user_query))

        # 构建完整提示词时，确保加入文件内容
        context = st.session_state.file_summary if st.session_state.file_summary else st.session_state.file_content
        full_prompt = f"""
        你是一个智能问答助手。
        {"以下是参考内容：" + context if context else ""}  # 关键：将文件内容/概括作为上下文
        用户问题：{user_query}
        """

        # 如果启用记忆，获取历史对话
        if use_memory:
            chat_history = st.session_state.memory.load_memory_variables({})["chat_history"]
            # 将历史对话添加到消息列表
            for message in chat_history:
                if isinstance(message, HumanMessage):
                    st.session_state.messages.append(HumanMessage(content=message.content))
                elif isinstance(message, AIMessage):
                    st.session_state.messages.append(AIMessage(content=message.content))

        # 构建请求消息列表
        messages = [{"role": "user" if isinstance(msg, HumanMessage) else "assistant",
                     "content": msg.content} for msg in st.session_state.messages]

        # 直接调用模型
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.post(
                f"{api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ).json()

            # 提取文本内容
            if "choices" in response and len(response["choices"]) > 0:
                response_text = response["choices"][0]["message"]["content"].strip()
            else:
                raise ValueError(f"无法解析响应格式: {response}")

        except Exception as e:
            response_text = f"调用模型失败: {str(e)}"

        # 调试模式下显示完整响应
        if st.session_state.debug_mode:
            st.subheader("📊 API 响应调试")
            st.json(response)

        # 添加回复到对话历史和记忆
        st.session_state.messages.append(AIMessage(content=response_text))
        if use_memory:
            st.session_state.memory.save_context(
                {"input": user_query},
                {"output": response_text}
            )

        # 显示回答
        st.subheader("💡 回答")
        st.markdown(response_text)
        st.divider()

    # 显示历史对话
    if st.session_state.messages:
        st.subheader("💬 对话历史")
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                st.markdown(f"**用户**: {msg.content}")
            else:
                st.markdown(f"**助手**: {msg.content}")

    # 底部信息
    st.markdown("---")
    st.markdown("© 2025 问答小助手 | 使用大语言模型构建")


if __name__ == "__main__":
    main()