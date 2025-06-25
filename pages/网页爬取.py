import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from pydantic import SecretStr
import re
import time

# 初始化OpenAI模型
openai_model = ChatOpenAI(
    model='gpt-4o-mini',
    base_url='https://api.openai-hk.com/v1/',
    api_key=SecretStr('hk-oh9hmp1000056169583738a8eeccd1d6810502b65832f931'),
)

# 初始化嵌入模型
embeddings = OpenAIEmbeddings(
    model='embedding-3',
    api_key=SecretStr('96aefc8f6386478e9bd07014e413ee2b.garDGiiQT1QPDpCu'),
    base_url='https://open.bigmodel.cn/api/paas/v4'
)

# 初始化session state
if 'web_analysis_history' not in st.session_state:
    st.session_state.web_analysis_history = []
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None


def crawl_web_page(url: str):
    """爬取网页内容并提取基本信息"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=10)
        response_time = time.time() - start_time
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "无标题"
        meta_description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={
            'name': 'description'}) else ""

        headings = []
        for level in ['h1', 'h2', 'h3']:
            for heading in soup.find_all(level):
                headings.append({"text": heading.get_text().strip(), "level": level})

        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]

        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                full_url = urljoin(base_url, href)
            elif href.startswith('http'):
                full_url = href
            else:
                continue

            link_text = a.get_text().strip() or "无文本"
            links.append({"text": link_text[:50] + "..." if len(link_text) > 50 else link_text, "url": full_url})

        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.startswith('/'):
                full_src = urljoin(base_url, src)
            elif src.startswith('http'):
                full_src = src
            else:
                continue
            images.append({"alt": img.get('alt', '无描述文本'), "src": full_src})

        return {
            "url": url,
            "status": response.status_code,
            "response_time": round(response_time, 2),
            "title": title,
            "meta_description": meta_description,
            "headings": headings,
            "paragraphs": paragraphs,
            "links": links[:20],
            "images": images[:10],
            "html": response.text[:5000] + "..." if len(response.text) > 5000 else response.text,
            "error": None
        }

    except requests.exceptions.RequestException as e:
        return {"url": url, "error": f"网络请求失败: {str(e)}"}
    except Exception as e:
        return {"url": url, "error": f"分析网页时出错: {str(e)}"}


def ai_analyze_content(content: str, analysis_type: str = "summary"):
    """使用AI分析网页内容"""
    try:
        if analysis_type == "summary":
            prompt = f"请为以下网页内容生成一个简洁的摘要，突出主要观点和关键信息:\n\n{content}"
        elif analysis_type == "sentiment":
            prompt = f"分析以下网页内容的情感倾向（积极/中性/消极），并解释原因:\n\n{content}"
        elif analysis_type == "keywords":
            prompt = f"从以下网页内容中提取5-10个关键词，并按重要性排序:\n\n{content}"
        elif analysis_type == "qa":
            prompt = f"基于以下网页内容，生成3个有深度的问题及其答案:\n\n{content}"
        else:
            prompt = f"请分析以下网页内容:\n\n{content}"

        response = openai_model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"AI分析失败: {str(e)}"


def create_vector_store_from_url(url: str):
    """从URL创建向量存储"""
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", "！", "？", "，", " "]
        )
        splits = text_splitter.split_documents(docs)
        vector_store = FAISS.from_documents(splits, embeddings)
        return vector_store
    except Exception as e:
        st.error(f"创建向量存储失败: {str(e)}")
        return None


def ask_question_about_web(question: str):
    """询问关于网页内容的问题"""
    if st.session_state.vector_store is None:
        return "请先分析一个网页"

    try:
        qa_chain = RetrievalQA.from_chain_type(
            llm=openai_model,
            chain_type="stuff",
            retriever=st.session_state.vector_store.as_retriever(),
            return_source_documents=True
        )

        prompt_template = """
        你是一个专业的网页内容分析师，请基于以下网页内容回答问题:
        {context}

        问题: {question}
        请给出详细、专业的回答:
        """
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        qa_chain.combine_documents_chain.llm_chain.prompt = PROMPT

        result = qa_chain({"query": question})
        return result["result"]
    except Exception as e:
        return f"查询失败: {str(e)}"


# Streamlit界面
st.set_page_config(page_title="智能网页分析工具", layout="wide")
st.title("🌐 智能网页分析工具")
st.caption("输入网页URL进行分析，然后可以直接提问关于网页内容的问题")

# URL输入和分析部分
url = st.text_input("请输入网页URL:", placeholder="https://example.com")

col1, col2 = st.columns(2)
with col1:
    analyze_btn = st.button("分析网页", use_container_width=True)
with col2:
    clear_btn = st.button("清除结果", use_container_width=True)

if clear_btn:
    st.session_state.current_analysis = None
    st.session_state.vector_store = None
    st.rerun()

if analyze_btn and url:
    with st.spinner("正在爬取和分析网页内容..."):
        crawl_result = crawl_web_page(url)

        if "error" in crawl_result and crawl_result["error"]:
            st.error(crawl_result["error"])
        else:
            st.session_state.vector_store = create_vector_store_from_url(url)

            with st.spinner("使用AI分析网页内容..."):
                content_text = "\n\n".join(crawl_result["paragraphs"][:10])
                st.session_state.current_analysis = {
                    **crawl_result,
                    "ai_summary": ai_analyze_content(content_text, "summary"),
                    "ai_sentiment": ai_analyze_content(content_text, "sentiment"),
                    "ai_keywords": ai_analyze_content(content_text, "keywords"),
                    "ai_qa": ai_analyze_content(content_text, "qa"),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }

# 显示分析结果
if st.session_state.current_analysis:
    analysis = st.session_state.current_analysis

    if st.button("保存分析结果", use_container_width=True):
        st.session_state.web_analysis_history.append(analysis)
        st.success("分析结果已保存!")

    st.success(f"网页分析完成! 状态码: {analysis['status']}, 响应时间: {analysis['response_time']}秒")

    # 基本信息
    with st.expander("📌 基本信息", expanded=True):
        st.subheader(analysis["title"])
        st.caption(analysis["url"])
        st.write(f"**Meta描述:** {analysis['meta_description'] or '无描述'}")
        st.write(f"**AI摘要:** {analysis['ai_summary']}")

    # 问答部分
    st.divider()
    st.subheader("💬 网页内容问答")
    question = st.text_input("关于网页内容有什么问题?", placeholder="例如: 这个网页的主要观点是什么?")

    if st.button("提问", use_container_width=True) and question:
        with st.spinner("正在思考..."):
            answer = ask_question_about_web(question)
            st.session_state.current_analysis["last_question"] = question
            st.session_state.current_analysis["last_answer"] = answer
            st.rerun()

    if "last_question" in st.session_state.current_analysis:
        st.markdown(f"**问题:** {st.session_state.current_analysis['last_question']}")
        st.markdown(f"**回答:** {st.session_state.current_analysis['last_answer']}")

    # 详细分析
    st.divider()
    st.subheader("🔍 详细分析")

    with st.expander("📊 内容分析", expanded=False):
        cols = st.columns(2)
        with cols[0]:
            st.write("**情感分析:**")
            st.write(analysis["ai_sentiment"])
        with cols[1]:
            st.write("**关键词提取:**")
            st.write(analysis["ai_keywords"])

    with st.expander("📝 生成问答", expanded=False):
        st.write(analysis["ai_qa"])

    with st.expander("📑 内容结构", expanded=False):
        st.write("**标题结构:**")
        for heading in analysis["headings"]:
            level = int(heading["level"][1])
            st.markdown(f"{'#' * level} {heading['text']}")

        st.write("**内容段落:**")
        for i, para in enumerate(analysis["paragraphs"][:5]):
            st.write(f"{i + 1}. {para}")

    with st.expander("🔗 链接和资源", expanded=False):
        cols = st.columns(2)
        with cols[0]:
            st.write("**相关链接:**")
            for link in analysis["links"][:10]:
                st.markdown(f"- [{link['text']}]({link['url']})")
        with cols[1]:
            st.write("**图片资源:**")
            for img in analysis["images"][:3]:
                st.image(img["src"], caption=img["alt"], width=200)

    with st.expander("📄 HTML源码预览", expanded=False):
        st.code(analysis["html"])

# 侧边栏历史记录
with st.sidebar:
    st.subheader("📚 历史记录")
    if st.session_state.web_analysis_history:
        for i, item in enumerate(reversed(st.session_state.web_analysis_history)):
            if st.sidebar.button(f"{i + 1}. {item['title'][:30]}...", key=f"hist_{i}"):
                st.session_state.current_analysis = item
                st.session_state.vector_store = create_vector_store_from_url(item["url"])
                st.rerun()
    else:
        st.sidebar.info("暂无历史记录")

    st.divider()
    st.caption("""
    **功能说明:**
    - 网页爬取与内容提取
    - AI内容分析(摘要/情感/关键词)
    - 基于内容的智能问答
    """)

# 页脚
st.divider()
st.caption("©智能网页分析工具 | 使用GPT-4和LangChain技术")