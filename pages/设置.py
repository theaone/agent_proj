import streamlit as st

# 初始化 session_state 中的 current_page 和 sub_page
if 'current_page' not in st.session_state:
    st.session_state.current_page = '我的账号'
if 'sub_page' not in st.session_state:
    st.session_state.sub_page = '我的账号'

# 页面样式定义
st.markdown(
    """
    <style>
        .main {
            background-color: #f0f8ff;
            font-family: "Microsoft YaHei", sans-serif;
        }
        .title {
            font-size: 24px;
            color: #333;
        }
        .subtitle {
            font-size: 18px;
            line-height:2.8;
            color: #666;
            margin-top: 20px;
        }
        .content {
            font-family:'Noto Serif CJK SC', serif; 
            line-height: 2.8;
            color: #000000;
            margin-top: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 用户账户类
class AccountSettings:
    def __init__(self, username, phone, email, registration_date):
        self.username = username
        self.phone = phone
        self.email = email
        self.registration_date = registration_date

    def display_info_on_web(self):
        """ 展示用户信息，并在为空时显示“未设置” """
        st.markdown('<div class="subtitle">用户信息</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="content">
                <strong>用户名:</strong> {self.username or '未设置'}<br>
                <strong>手机号:</strong> {self.phone or '未设置'}<br>
                <strong>邮箱:</strong> {self.email or '未设置'}<br>
                <strong>注册时间:</strong> {self.registration_date}
            </div>
        """, unsafe_allow_html=True)

    def clear_info(self):
        """ 清除用户信息 """
        self.username = None
        self.phone = None
        self.email = None

    def logout(self):
        """ 退出登录逻辑 """
        st.info("已退出登录")
        self.clear_info()

    def delete_account(self):
        """ 注销账户逻辑 """
        st.warning("账户已注销")
        self.clear_info()


# 创建 AccountSettings 实例
account = AccountSettings(
    username="RaccoonCharlotte",
    phone="178****8924",
    email=None,
    registration_date="2025-06-24"
)

# 侧边栏导航
with st.sidebar:
    with st.expander("我的账号", expanded=st.session_state.current_page == "我的账号"):
        if st.button("我的账号", key="info_me"):
            st.session_state.current_page = '我的账号'
            st.session_state.sub_page = '我的账号'
    with st.expander("快捷键", expanded=st.session_state.current_page == "快捷键"):
        if st.button("快捷键", key="quick_key"):
            st.session_state.current_page = '快捷键'
            st.session_state.sub_page = '快捷键'
    with st.expander("关于", expanded=st.session_state.current_page == "关于"):
        if st.button("关于", key="about"):
            st.session_state.current_page = '关于'
            st.session_state.sub_page = '关于'

# 右侧内容区
if st.session_state.sub_page == "我的账号":
    st.markdown('<div class="title">我的账号</div>', unsafe_allow_html=True)
    account.display_info_on_web()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("退出登录", key="logout_button"):
            account.logout()
            st.switch_page("主页.py")  # 跳转到主页
    with col2:
        if st.button("注销账户", key="delete_account_button"):
            account.delete_account()
            st.switch_page("主页.py")  # 跳转到主页

elif st.session_state.sub_page == "快捷键":
    st.markdown('<div class="title">快捷键</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">常用操作快捷键</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="content">
        | 功能 | 快捷键 |<br>
        |------|--------|<br>
        | 快速对话 | Ctrl + L |<br>
        | 快速搜索 | Ctrl + K |<br>
        | 开/关侧边栏 | Ctrl + B |<br>
        | 粗体 | Ctrl + B |<br>
        | 斜体 | Ctrl + I |<br>
        | 下划线 | Ctrl + U |<br>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.sub_page == "关于":
    st.markdown('<div class="title">关于我们</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="content">
        <center>「ai小智」</center>是一款将AI大模型的能力与文档翻译、数据分析场景深度结合的工具型产品，
        致力于为用户提供一站式创作平台和知识管理空间。
        用户可以通过对话式的交互，完成信息的实时翻译、文档的撰写编辑、数据的处理分析。<br>

        <center>「小智团队」</center>AI 小智团队是一支专注于AI 智能体数据分析的创新型研究团队，致力于探索人工智能与数据科学的深度融合，
        通过构建高效的智能体模型与数据分析框架，解决复杂场景下的数据挖掘、模式识别及决策优化问题。
        团队以 “数据驱动智能，智能赋能数据” 为核心理念，聚焦于智能体在动态数据环境中的学习、推理与自适应分析能力，
        推动 AI 技术在金融、医疗、工业等领域的实际应用。
        </div>
    """, unsafe_allow_html=True)
