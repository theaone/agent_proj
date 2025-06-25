
import os
import streamlit as st

# 页面配置
st.set_page_config(page_title='ai小智', page_icon='🤖')

# 自定义样式
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f8ff;
        font-family: "Microsoft YaHei", sans-serif;
    }
    .custom-link h4 {
        color: black; 
        transition: color 0.3s ease;
        margin: 0;
    }
    .custom-link:hover h4,
    .custom-link:focus h4 {
        color: blue;
        text-decoration: underline;
    }
    .top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 欢迎信息
st.title('你好，我是ai小智~o(〃' '〃)o')
st.write('我能运用语言模型，进行问答、生成图表、提供翻译，欢迎与我进行对话，了解更多用法哦！')

# 展示图片 1.png
current_dir = os.path.dirname(__file__)
image_path = os.path.join(current_dir, "images", "1.png")

if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

# 创建顶部并列布局
col1, col2 = st.columns([1, 1])

# "了解ai小智"跳转卡片
with col1:
    st.markdown(
        """
        <div style="margin-top: 10px; cursor: pointer;" class="custom-link" onclick="document.getElementById('hidden_button').click()">
            <h4>了解 ai 小智</h4>
        </div>
        <button id="hidden_button" style="display:none;"></button>
        """,
        unsafe_allow_html=True
    )

    if st.button("点此跳转", key="goto_intro", help="跳转到介绍页"):
        st.switch_page("pages/介绍.py")  # 替换为实际路径

# "我的文档"模块 + 功能选择下拉框
with col2:
    st.subheader('我的文档')

    # 功能选择下拉框
    selected_option = st.selectbox(
        "📁 上传文件",
        ["", "小智问答", "小智翻译", "网页爬取","数据分析", '图像处理','数据可视化']
    )

    if selected_option == "小智问答":
        st.switch_page("pages/小智问答.py")
    elif selected_option == "小智翻译":
        st.switch_page("pages/小智翻译.py")
    elif selected_option == "数据分析":
        st.switch_page("pages/数据分析.py")
    elif selected_option == '图像处理':
        st.switch_page("pages/网页爬取.py")
    elif selected_option == '网页爬取':
        st.switch_page("pages/图像处理.py")
    elif selected_option == '数据可视化':
        st.switch_page("pages/数据可视化.py")

# 展示图片 2.png 并与虚线框对齐
image_path_2 = os.path.join(current_dir, "images", "2.png")
if os.path.exists(image_path_2):
    st.image(image_path_2)
else:
    st.error("图片 2.png 未找到")

# 添加快捷键说明
st.markdown("""
    <div style="margin-top: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
        <h4>快捷键说明：</h4>
        <ul>
            <li>Ctrl+L: 跳转到小智问答</li>
            <li>Ctrl+K: 返回主页</li>
            <li>Ctrl+B: 跳转到小智翻译</li>
            <li>Ctrl+I: 跳转到图像处理</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# 使用JavaScript实现全局快捷键
st.markdown("""
<script>
const shortcuts = {
    "KeyL": "pages/小智问答.py",
    "KeyK": "主页.py",
    "KeyB": "pages/小智翻译.py",
    "KeyI": "pages/图像处理.py"
};

document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && shortcuts[e.code]) {
        window.location.href = shortcuts[e.code];
    }
});
</script>
""", unsafe_allow_html=True)