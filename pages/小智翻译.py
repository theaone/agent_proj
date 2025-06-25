import streamlit as st
import requests
import chardet
import pandas as pd
import io
from pydantic import SecretStr
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# 【必加】每页独立设置标题（否则会继承主入口标题）
st.set_page_config(
    page_title="小智翻译",
    page_icon="🌐",
    layout="wide"
)

# 初始化会话状态（用于存储对话历史和内存对象）
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history")

if "messages" not in st.session_state:
    st.session_state.messages = []


# 翻译功能核心代码（添加记忆模块）
def main():
    st.title("智能翻译助手 🤖")
    st.markdown("基于大语言模型的智能翻译工具，支持多语言互译和对话记忆功能")

    # 侧边栏配置
    with st.sidebar.expander("📡 模型配置", expanded=True):
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
            help="温度越高，输出越随机；越低越确定"
        )
        # 记忆功能开关
        use_memory = st.checkbox("启用对话记忆", value=True,
                                 help="保留历史对话上下文，让模型理解连续请求")
        if use_memory:
            st.info("💡 对话记忆已启用，模型会记住之前的翻译内容")
            # 清空记忆按钮
            if st.button("🧹 清空对话历史"):
                st.session_state.memory.clear()
                st.session_state.messages = []
                st.success("对话历史已清空")

    # 语言选择
    col1, col2 = st.columns(2)
    with col1:
        from_lang = st.selectbox(
            "源语言",
            ["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文"]
        )
    with col2:
        to_lang = st.selectbox(
            "目标语言",
            ["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文"]
        )

    # 文本输入和文件上传选择
    input_option = st.radio("选择输入方式", ["文本输入", "文件上传"])
    text_input = ""
    if input_option == "文本输入":
        text_input = st.text_area(
            "📝 请输入需要翻译的文本",
            height=150,
            placeholder="在这里输入需要翻译的文本..."
        )
    else:
        uploaded_file = st.file_uploader("📁 上传需要翻译的文件", type=["txt", "md", "csv", "xlsx"])
        if uploaded_file:
            file_extension = uploaded_file.name.split(".")[-1].lower()
            raw_data = uploaded_file.read()  # 读取文件的二进制数据
            # 检测文件编码
            detect_result = chardet.detect(raw_data)
            encoding = detect_result.get('encoding', 'utf-8')
            try:
                if file_extension == "txt" or file_extension == "md":
                    text_input = raw_data.decode(encoding)
                    st.text_area("文件内容预览", text_input, height=150)
                elif file_extension == "csv":
                    decoded_data = raw_data.decode(encoding)
                    df = pd.read_csv(io.StringIO(decoded_data))
                    text_input = " ".join([str(cell) for row in df.values for cell in row])
                    st.text_area("文件内容预览", text_input, height=150)
                elif file_extension == "xlsx":
                    decoded_data = raw_data.decode(encoding)
                    byte_data = decoded_data.encode(encoding)
                    df = pd.read_excel(io.BytesIO(byte_data))
                    text_input = " ".join([str(cell) for row in df.values for cell in row])
                    st.text_area("文件内容预览", text_input, height=150)
            except UnicodeDecodeError:
                st.error(f"尝试以 {encoding} 编码解码文件失败，请尝试其他文件")
                text_input = ""

    # 带记忆的翻译函数
    def translate_text():
        if not text_input.strip():
            st.warning("请输入或上传需要翻译的文本内容")
            return

        # 构建完整提示词（包含语言信息）
        full_prompt = f"请将以下{from_lang}文本翻译成{to_lang}：\n{text_input}"

        # 添加用户输入到对话历史
        st.session_state.messages.append(HumanMessage(content=full_prompt))

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

        # 调用模型
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
            with st.spinner("正在翻译..."):
                response = requests.post(
                    f"{api_base}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                translation = result["choices"][0]["message"]["content"].strip()

                # 添加回复到对话历史和记忆
                st.session_state.messages.append(AIMessage(content=translation))
                if use_memory:
                    st.session_state.memory.save_context(
                        {"input": full_prompt},
                        {"output": translation}
                    )

                return translation
        except Exception as e:
            return f"翻译失败：{str(e)}"

    # 显示历史对话
    if st.session_state.messages and use_memory:
        st.subheader("对话历史 📜")
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                st.markdown(f"**用户**: {msg.content}")
            else:
                st.markdown(f"**模型**: {msg.content}")
        st.divider()

    # 翻译按钮
    if st.button("🚀 开始翻译", type="primary", use_container_width=True):
        translation = translate_text()
        if translation:
            st.subheader("翻译结果 🔍")
            st.text_area(
                "结果",
                value=translation,
                height=150,
                disabled=True
            )
            st.code(translation)
            st.success("翻译完成！可复制结果")

    # 底部信息
    st.markdown("---")
    st.markdown("© 2025 智能翻译助手 | 使用大语言模型构建")


# 【必加】每页必须通过主函数执行
if __name__ == "__main__":
    main()