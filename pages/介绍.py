import os
import streamlit as st

# 初始化会话状态
if 'current_page' not in st.session_state:
    st.session_state.current_page = '欢迎'
if 'sub_page' not in st.session_state:
    st.session_state.sub_page = '欢迎介绍'

# 页面配置
st.set_page_config(page_title="关于 ai小智", page_icon="🤖")

# 自定义 CSS 样式
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
            text-indent:2em;
            margin-top: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 侧边栏导航
with (st.sidebar):
    # 二级目录
    with st.expander("欢迎", expanded=st.session_state.current_page == "欢迎"):
        if st.button("欢迎介绍", key="welcome_intro"):
            st.session_state.current_page = '欢迎'
            st.session_state.sub_page = '欢迎介绍'

    with st.expander("小智翻译", expanded=st.session_state.current_page == "小智翻译"):
        if st.button("模块介绍", key="translate_intro"):
            st.session_state.current_page = '小智翻译'
            st.session_state.sub_page = '模块介绍'
        if st.button("工作台介绍", key="translate_workbench"):
            st.session_state.current_page = '小智翻译'
            st.session_state.sub_page = '工作台介绍'
        if st.button("操作步骤", key="translate_steps"):
            st.session_state.current_page = '小智翻译'
            st.session_state.sub_page = '操作步骤'
        if st.button("示例运行", key="translate_example"):
            st.session_state.current_page = '小智翻译'
            st.session_state.sub_page = '示例运行'

    with st.expander("小智问答", expanded=st.session_state.current_page == "小智问答"):
        if st.button("问答介绍", key="question_intro"):
            st.session_state.current_page = '小智问答'
            st.session_state.sub_page = '问答介绍'
        if st.button("模型介绍", key="question_model"):
            st.session_state.current_page = '小智问答'
            st.session_state.sub_page = '模型介绍'
        if st.button("工作台介绍", key="question_workbench"):
            st.session_state.current_page = '小智问答'
            st.session_state.sub_page = '工作台介绍'
        if st.button("操作步骤", key="question_steps"):
            st.session_state.current_page = '小智问答'
            st.session_state.sub_page = '操作步骤'
        if st.button("示例运行", key="question_example"):
            st.session_state.current_page = '小智问答'
            st.session_state.sub_page = '示例运行'

    with st.expander("数据分析", expanded=st.session_state.current_page == "数据分析"):
        if st.button("分析介绍", key="analysis_intro"):
            st.session_state.current_page = '数据分析'
            st.session_state.sub_page = '分析介绍'

    with st.expander("图像处理", expanded=st.session_state.current_page == "图像处理"):
        if st.button("处理介绍", key="image_intro"):
            st.session_state.current_page = '图像处理'
            st.session_state.sub_page = '图像介绍'
        if st.button("模型介绍", key="image_model"):
            st.session_state.current_page = '图像处理'
            st.session_state.sub_page = '模型介绍'
        if st.button("工作台介绍", key="image_workbench"):
            st.session_state.current_page = '图像处理'
            st.session_state.sub_page = '工作台介绍'
        if st.button("操作步骤", key="imagen_steps"):
            st.session_state.current_page = '图像处理'
            st.session_state.sub_page = '操作步骤'
        if st.button("示例运行", key="image_example"):
            st.session_state.current_page = '图像处理'
            st.session_state.sub_page = '示例运行'

    with st.expander("网页爬取", expanded=st.session_state.current_page == "网页爬取"):
        if st.button("功能介绍", key="web_intro"):
            st.session_state.current_page = '网页爬取'
            st.session_state.sub_page = '功能介绍'
        if st.button("工作台介绍", key="web_workbench"):
            st.session_state.current_page = '网页爬取'
            st.session_state.sub_page = '工作台介绍'
        if st.button("操作步骤", key="web_steps"):
            st.session_state.current_page = '网页爬取'
            st.session_state.sub_page = '操作步骤'
        if st.button("示例运行", key="web_example"):
            st.session_state.current_page = '网页爬取'
            st.session_state.sub_page = '示例运行'

    with st.expander("数据可视化", expanded=st.session_state.current_page == "数据可视化"):
        if st.button("可视化介绍", key="show_intro"):
            st.session_state.current_page = '数据可视化'
            st.session_state.sub_page = '可视化介绍'
        if st.button("使用指南", key="show_kill"):
            st.session_state.current_page = '数据可视化'
            st.session_state.sub_page = '使用指南'
        if st.button("操作步骤", key="show_steps"):
            st.session_state.current_page = '数据可视化'
            st.session_state.sub_page = '操作步骤'
        if st.button("示例运行", key="show_example"):
            st.session_state.current_page = '数据可视化'
            st.session_state.sub_page = '示例运行'


# 主内容区域
if st.session_state.current_page == "欢迎":
    st.title('欢迎来到 ai小智')
    st.markdown("<div class='title'>一、ai小智的背景介绍</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="content">
            ai小智是一款将AI大模型的能力与文档翻译、数据分析场景深度结合的工具型产品，致力于为用户提供一站式创作平台和知识管理空间。
            用户可以通过对话式的交互，完成信息的实时翻译、文档的撰写编辑、数据的处理分析。<br>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='title'>二、ai小智的前世今生</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="content">
            <strong>ai小智诞生</strong>于 2025 年 6 月 25 日，是一款专注于数据分析的工具型产品。依托强大的模型能力和工程化手段，ai小智不仅具备数据归纳、推理和分析功能，还能实现表格整理和图表生成，可提供全方位的数据分析支持，完成数据清洗、运算、比较分析、趋势预测及数据可视化等数据分析任务。<br>
            <strong>ai小智的深入发展</strong>，我们将数据分析定位为办公场景中的一个重要环节，从初步计划的生成，到文本材料、数据文件的深入分析，再到最终的内容创作和定稿，小智致力于用 AI 赋能整个工作流程，从单一的数据分析工具进化为具备[文理大脑]的创作空间<br>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='title'>三、ai小智的愿景<br></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="content">
            <strong>ai小智的愿景</strong>是成为全球最智能的数据分析工具，为用户提供一站式创作平台和知识管理空间。<br>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='title'>四、ai小智的团队</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="content">
            ai小智开发团队由余彦蓉、邓霞、刘玲、赫文晶等四名成员组成
        </div>
        """,
        unsafe_allow_html=True
    )

# 小智翻译页面内容
elif st.session_state.current_page == "小智翻译":
    st.title('欢迎来到小智翻译')

    # 模块介绍
    if st.session_state.sub_page == '模块介绍':
        st.markdown("<div class='title'>小智翻译</div><br>", unsafe_allow_html=True)
        st.markdown("""
                    <div class="content">
                        <strong>小智翻译</strong>于2025年6月24日重磅推出，是一款基于大语言模型构建的多语言互译工具，支持文本输入与文件上传两种方式，可实现中、英、日、韩、法、德、西班牙语等多种语言之间的高质量互译。<br>
                        <strong>⚙️ 主要功能模块<br></strong>
                        1. 模型配置（侧边栏）<br>
                        - API 地址设置：自定义大模型服务地址，默认为 'https://open.bigmodel.cn/api/paas/v4'<br>
                        - API 密钥输入：用于身份验证的密钥（隐藏显示）<br>
                        - 模型选择：支持 'glm-4-air, 'glm-4', 'chatglm-pro' 等模型<br>
                        - 生成温度调节：控制输出随机性（0.0 ~ 1.0）<br>
                        2. 语言选择<br>
                        - 源语言：中文 / 英文 / 日文 / 韩文 / 法文 / 德文 / 西班牙文<br>
                        - 目标语言：同上，支持任意组合互译<br>
                        3. 输入方式
                        - ✍️ 文本输入：直接在文本框中粘贴需要翻译的内容<br>
                        - 📁 文件上传：<br>
                        - 支持格式：'.txt' '.md', '.csv', '.xlsx'<br>
                        - 自动检测编码（如 UTF-8）<br>
                        - 可读取并翻译文件中的文本内容（CSV/XLSX 单元格拼接）<br>
                         4. 翻译执行<br>
                        - 点击“🚀 开始翻译”按钮后，系统自动调用模型接口进行翻译<br>
                        - 实时加载动画提示“正在翻译...”<br>
                        - 显示翻译结果，并支持复制操作<br>

                    </div>
                """, unsafe_allow_html=True)


    if st.session_state.sub_page == "工作台介绍":
        st.markdown("<div class='title'>1.工作台介绍</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class="content">
                这里是小智翻译的工作台介绍内容，包含界面布局、功能模块说明等。
            </div>
        """, unsafe_allow_html=True)
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '3.png'))
        st.image(image_path, caption="小智翻译主界面示意图", use_container_width=True)
        # 图片介绍内容
        st.markdown(""" <div class="content">
            小智翻译的主界面布局。左侧为模型配置与语言选择区域，支持API地址设置、密钥输入及源/目标语言切换；
            右侧为输入输出区域，用户可在此粘贴文本或上传文件进行翻译处理。
        </div>""", unsafe_allow_html=True)
        

    elif st.session_state.sub_page == "操作步骤":
        st.markdown("<div class='title'>操作步骤</div><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="content">
                这里是小智翻译的操作步骤说明，包括如何输入文本、选择语言、调用模型等。
            </div>
        """, unsafe_allow_html=True)
        # 添加图片4
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '4.png'))
        st.image(image_path, caption="翻译步骤1", use_container_width=True)
        st.markdown(""" <div class="content">
            步骤一：根据翻译的内容要求，选择不同翻译模型，同时勾选“启用对话记忆”，使模型记忆上下文对话.
        </div>""", unsafe_allow_html=True)
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '5.png'))
        st.image(image_path, caption="翻译步骤2", use_container_width=True)
        st.markdown(""" <div class="content">
            步骤二：选择源语言和目标语言，并输入需要翻译的文本或上传文件。
        </div>""", unsafe_allow_html=True)
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '6.png'))
        st.image(image_path, caption="翻译步骤3", use_container_width=True)
        st.markdown(""" <div class="content">
            步骤三：点击“🚀 启动翻译”按钮，系统将调用模型接口进行翻译，并实时显示翻译结果。
        </div>""", unsafe_allow_html=True)

    elif st.session_state.sub_page == "示例运行":
        st.markdown("<div class='title'>示例运行</div><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="content">
                这里是小智翻译的示例运行部分，你可以查看一个完整的翻译流程演示。
            </div>
        """, unsafe_allow_html=True)
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '7.png'))
        st.image(image_path, caption="示例运行", use_container_width=True)
        st.markdown(""" <div class="content">
            示例运行：用户上传文件，选择中文翻译为英语，点击“🚀 启动翻译”按钮，系统将调用模型接口进行翻译，并实时显示翻译结果。
        </div>""", unsafe_allow_html=True)
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '8.png'))
        st.image(image_path, caption="历史对话", use_container_width=True)
        st.markdown(""" <div class="content">
            系统将翻译后的历史结果保存在文件中，并显示在界面上。
        </div>""", unsafe_allow_html=True)

# 小智问答页面内容
elif st.session_state.current_page == "小智问答":
    st.title('欢迎来到小智问答')

    if st.session_state.sub_page == "问答介绍":
        st.markdown("<div class='title'>问答介绍</div><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="content">
                小智问答是一款基于大语言模型的智能问答系统，能够理解自然语言并提供准确的回答。<br>
                主要功能包括：<br>
                - 知识问答：回答各类知识型问题<br>
                - 文档问答：基于上传文档进行问答，支持上传 .txt, .md, .csv, .xlsx 文件<br>
                - 代码生成：根据需求生成代码片段<br>
                - 创意写作：辅助进行文案创作<br>
                此外，系统还支持对话记忆功能，可以记住历史对话上下文，提供更连贯的交互体验。<br>
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.sub_page == "模型介绍":
        st.markdown("<div class='title'>模型介绍</div><br>", unsafe_allow_html=True)
        st.markdown(""" <div class="content">
                    在小智问答中，我们提供了三个模型，分别是glm-4、glm-4-air、chatglm-pro<br>
                    <center><strong>1.glm-4</strong></center>
                    <strong>长上下文与精准召回</strong>：支持 128K 上下文窗口长度，单次可处理文本达 300 页，在 “大海捞针” 压力测试（128K 文本长度内），精度召回近乎 100%，长文本全局信息不失焦 。<br>
                    <strong>推理快、成本低</strong>,在中文专业能力、理解能力和角色扮演等方面极优 ；多任务语言理解、提示词 / 指令跟随等基准测试，以及 GSM8K、Math 等数据集上，表现优于 GPT-3.5 。<br>
                    <strong>自主理解、规划复杂指令，自由调用网页浏览器、代码解释器、多模态文生图大模型</strong>等。可处理数据分析、图表绘制、PPT 生成等任务，用自动化解决提示词复杂痛点 ，如结合网页浏览、文生图、代码解释器等多工具自动调用。<br>
                    <strong>文生图和多模态理解增强</strong>，文生图模型 CogView3 在多个评测指标上，达到 DALLE3 的 91.4% - 99.3% 水平 。<br>
                    <center><strong>2.glm-4</strong></center>
                    <strong>参数与性能平衡</strong>：320 亿参数，以 1/3 参数量实现与更大模型相媲美的性能，像 “小钢炮”，为智能体大规模落地提供新选择 。<br>
                    <strong>工具调用高效</strong>：多轮指令执行速度比主流模型快 2 倍，支持多轮复杂指令快速执行，API 调用成功率提升 60% 。<br>
                    <strong>联网搜索优质</strong>：联网搜索准确率提升 47%，可突破信息孤岛，支持动态数据抓取，做实时信息捕手 。<br>
                    <strong>代码生成出色</strong>：生成代码通过率超 90% ，语法正确率达 92% ，支持 30 + 编程语言，还能自动修复常见 bug，堪称代码外科医生 。<br>
                    <strong>多任务与优化</strong>：可同时处理 NLP、逻辑推理等多样化智能体任务；通过优化预训练数据（融合代码库、数学推导等结构化数据）、对齐策略（采用 RLHF 方法优化工具调用等核心能力 ），以及稀疏注意力机制实现高性能 。<br>
                    <center><strong>3.chatglm-pro</center></strong>
                    在智能对话、中文理解等方面有基础能力，能较好理解用户意图，进行自然语言交互，延续智谱模型在中文处理等方面的优势 。</div>""", unsafe_allow_html=True)
    elif st.session_state.sub_page == "工作台介绍":
        st.markdown("<div class='title'>1.工作台介绍</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class="content">
                这里是小智问答的工作台介绍内容，包含界面布局、功能模块说明等。
            </div>
        """, unsafe_allow_html=True)
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '9.png'))
        st.image(image_path, caption="小智问答主界面示意图", use_container_width=True)
        st.markdown(""" <div class="content">
            小智问答的主界面布局。左侧为模型配置区域，支持API地址设置、密钥输入、模型选择以及对话记忆和调试选项的选择；
            右侧为输入输出区域，用户可在此粘贴文本或上传文件进行问答处理。
        </div>""", unsafe_allow_html=True)
    elif st.session_state.sub_page == "操作步骤":
        st.markdown("<div class='title'>操作步骤</div><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="content">
                这里是小智问答的操作步骤说明，包括如何上传文件、生成提问、调用模型等。
            </div>
        """, unsafe_allow_html=True)
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '10.png'))
        st.image(image_path, caption="操作步骤1", use_container_width=True)
        st.markdown(""" <div class="content">
            步骤一：根据问答的内容要求，配置相关api设定，选择不同问答模型、生成温度，同时勾选“启用对话记忆”，使模型记忆上下文对话.<br></div>""", unsafe_allow_html=True)
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '11.png'))
        st.image(image_path, caption="操作步骤2", use_container_width=True)
        st.markdown(""" <div class="content">
            步骤二：根据需要直接提问或者上传对应文件，在上传的文件中，提供了有关“简要概述、详细摘要、关键要点”在内的三个文件概括级别。
        </div>""", unsafe_allow_html=True)
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '12.png'))
        st.image(image_path, caption="操作步骤3", use_container_width=True)
        st.markdown(""" <div class="content">
            步骤三：点击“🚀 启动问答”按钮，系统将调用模型接口进行问答，并实时显示结果。
        </div>""", unsafe_allow_html=True)
    elif st.session_state.sub_page == "示例运行":
        st.markdown("<div class='title'>1.直接提问示例运行</div><br>", unsafe_allow_html=True)
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '13.png'))
        st.image(image_path, caption="直接提问示例运行", use_container_width=True)
        st.markdown("""
        <div class="content">直接在提问框内，输入我想询问的内容，得到对应结果</div
        """, unsafe_allow_html=True)
        st.markdown("<div class='title'>2.上传文件提问示例运行</div><br>",unsafe_allow_html=True)
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '14.png'))
        st.image(image_path, caption="上传文件提问示例运行", use_container_width=True)
        st.markdown("""
        <div class="content">上传文件，并选择对应的文件类型，根据你的文件内容，进行提问，得到对应结果，如果回答内容不理想，可以尝试修改提示词或者选择其他模型</div
        """, unsafe_allow_html=True)

# 图像处理页面内容
elif st.session_state.current_page == "图像处理":
    st.title('欢迎来到图像处理')

    if st.session_state.sub_page == "图像介绍":
        st.markdown("<div class='title'>一、图像处理模块介绍</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='content'>
                <strong>图像处理助手</strong>是一款基于大语言模型与计算机视觉技术构建的智能图像分析工具，
                支持用户上传图像并自动识别其中的物体、场景、人物等元素，并进行分类与标注。
                该工具可广泛应用于：<br>
                - 安防监控：识别可疑行为或目标<br>
                - 医疗影像诊断：辅助医生分析病灶区域<br>
                - 自动驾驶：识别道路环境与障碍物<br>
                - 教育科研：图像理解与内容归纳<br>
                <br>
                功能亮点：<br>
                - 支持多种图像格式（JPG/PNG/JPEG）<br>
                - 多模态大模型识别图像内容<br>
                - 自动标注与置信度显示<br>
                - 可视化展示识别结果<br>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif st.session_state.sub_page == "模型介绍":
        st.markdown("<div class='title'>二、支持的模型介绍</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='content'>
                <center><strong>1.glm-4v</strong></center>
                <strong>多模态能力</strong>：GLM-4V 是智谱 AI 推出的多模态大模型，支持图像输入与文本理解相结合。<br>
                <strong>高精度识别</strong>：对图像中的文字、物体、场景具有较高的识别准确率。<br>
                <strong>上下文记忆</strong>：支持对话历史记忆，便于连续提问与推理。<br>
                <strong>中文优化</strong>：在中文图像理解和描述生成方面表现优异。<br>
                <br>
                <center><strong>2.GPT-4 Vision</strong></center>
                <strong>OpenAI 官方图像模型</strong>：提供强大的图像理解能力，适用于复杂场景分析。<br>
                <strong>全球通用性强</strong>：支持多语言输出，适用于国际项目协作。<br>
                <strong>灵活集成</strong>：可通过 API 快速接入现有系统，实现端到端图像处理流程。<br>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif st.session_state.sub_page == "工作台介绍":
        st.markdown("<div class='title'>三、工作台介绍</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='content'>
                这里是图像处理的工作台介绍内容，包含界面布局、功能模块说明等。
            </div>
            """,
            unsafe_allow_html=True
        )
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '15.png'))
        st.image(image_path, caption="图像处理主界面示意图", use_container_width=True)
        st.markdown(
            """<div class='content'>
                图像处理主界面分为左右两部分：<br>
                - 左侧：模型配置区，可设置API地址、密钥、模型选择及调试选项<br>
                - 右侧：图像上传与结果显示区，用户可上传图像并查看分析结果<br>
            </div>""",
            unsafe_allow_html=True
        )

    elif st.session_state.sub_page == "操作步骤":
        st.markdown("<div class='title'>四、操作步骤</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='content'>
                这里是图像处理的操作步骤说明，包括如何上传图像、调用模型、查看分析结果等。
            </div>
            """,
            unsafe_allow_html=True
        )
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '16.png'))
        st.image(image_path, caption="步骤一：上传图像", use_container_width=True)
        st.markdown(
            """<div class='content'>
                步骤一：点击“📁 上传图像进行分析”，选择支持格式的图像文件（JPG/PNG/JPEG）。
            </div>""",
            unsafe_allow_html=True
        )

        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '17.png'))
        st.image(image_path, caption="步骤二：开始分析", use_container_width=True)
        st.markdown(
            """<div class='content'>
                步骤二：点击“🔍 开始分析图像”按钮，系统将调用模型接口进行图像识别与分析。
            </div>""",
            unsafe_allow_html=True
        )

        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '18.png'))
        st.image(image_path, caption="步骤三：查看结果", use_container_width=True)
        st.markdown(
            """<div class='content'>
                步骤三：系统返回图像分析结果，并展示自动标注信息（如人、汽车、建筑物等）及其置信度。
            </div>""",
            unsafe_allow_html=True
        )

    elif st.session_state.sub_page == "示例运行":
        st.markdown("<div class='title'>五、示例运行</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='content'>
                下面是一个完整的图像处理流程示例：
            </div>
            """,
            unsafe_allow_html=True
        )
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '19.jpeg'))
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '20.png'))
        st.image(image_path, caption="示例图像：城市街景", use_container_width=True)
        st.markdown(
            """<div class='content'>
                示例一：上传一张城市街景图像，包含行人、车辆、建筑等元素。
            </div>""",
            unsafe_allow_html=True
        )

        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '21.png'))
        st.image(image_path, caption="分析结果展示", use_container_width=True)
        st.markdown(
            """<div class='content'>
                示例二：点击“🔍 开始分析图像”后，系统返回如下结果：<br>
                - 识别出“人”、“汽车”、“建筑物”<br>
                - 显示各对象的置信度（92%、85%、90%）<br>
                - 提供图像整体描述，如“繁忙的城市街道，有行人和车辆通行”
            </div>""",
            unsafe_allow_html=True
        )


# 在数据分析页面内容下方或其他功能模块并列的位置添加：
elif st.session_state.current_page == "网页爬取":
    st.title('欢迎来到网页爬取')

    if st.session_state.sub_page == "功能介绍":
        st.markdown("<div class='title'>一、网页爬取模块介绍</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='content'>
                <strong>网页爬取助手</strong>
                是一款基于大语言模型与网络数据抓取技术构建的智能工具，通过Streamlit 智能网页分析工具，其核心功能围绕着网页内容的抓取、分析和问答展开。
                支持用户输入指定网址自动获取目标网页的核心内容，并提供信息提取与分析服务。
                该工具可广泛应用于：<br>
                - 数据采集：快速抓取公开网站上的数据<br>
                - 内容监控：实时跟踪特定网页内容变化<br>
                - 舆情分析：收集社交媒体或新闻平台上的舆论信息<br>
                - 智能问答：为后续的问答模块提供基础数据支持<br>
                <br>
                功能亮点：<br>
                <strong>- 自动化爬取网页内容，提取关键信息</strong><br>
                使用 requests 发送 HTTP 请求获取网页 HTML 内容；使用 BeautifulSoup 解析 HTML，提取以下信息：<br>
                网页标题（title）<br>
                Meta 描述<br>
                主要标题（h1, h2, h3）<br>
                段落文本<br>
                超链接（处理相对路径并转换为绝对路径）<br>
                <strong>- 支持AI生成摘要和关键词</strong><br>
                利用 langchain_openai.ChatOpenAI 接口调用 GPT 模型进行 AI 分析：对网页内容生成简洁摘要；提取 3~5 个关键词。支持错误处理，如网络异常或模型调用失败时返回提示。<br>
                <strong>- 基于向量数据库实现精准问答</strong><br>
                使用 WebBaseLoader 加载网页内容，通过 RecursiveCharacterTextSplitter 进行文本分块，借助 FAISS 构建本地向量数据库，支持后续语义检索。利用 RetrievalQA 链结合 FAISS 向量数据库，实现基于网页内容的问答。自定义提示模板，提升回答准确性。
            </div>
            """,
            unsafe_allow_html=True
        )

    elif st.session_state.sub_page == "工作台介绍":
        st.markdown("<div class='title'>二、工作台介绍</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='content'>
                这里是网页爬取的工作台介绍内容，包含界面布局、功能模块说明等。
            </div>
            """,
            unsafe_allow_html=True
        )
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '22.png'))
        st.image(image_path, caption="网页爬取主界面示意图", use_container_width=True)
        st.markdown(
            """<div class='content'>
                网页爬取主界面分为上下两部分：<br>
                - 上部：URL输入区，用户可粘贴需要爬取的目标网页地址<br>
                - 下部：结果展示区，显示网页的基本信息、AI分析结果及相关资源链接<br>
            </div>""",
            unsafe_allow_html=True
        )

    elif st.session_state.sub_page == "操作步骤":
        st.markdown("<div class='title'>三、操作步骤</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='content'>
                这里是网页爬取的操作步骤说明，包括如何输入URL、执行爬取、查看分析结果等。
            </div>
            """,
            unsafe_allow_html=True
        )
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '23.png'))
        st.image(image_path, caption="网页分析步骤详解", use_container_width=True)
        st.markdown(
            """<div class='content'>
                步骤一：在文本框中输入目标网页的完整URL（如 https://example.com）。<br>
                步骤二：点击“分析网页”按钮，系统将自动爬取目标网页并提取基本信息。<br>
                步骤三：系统返回网页分析结果，包括标题、描述、段落内容以及相关链接等信息。<br>
            </div>""",
            unsafe_allow_html=True
        )
        image_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '24.png'))
        st.image(image_path, caption="网页内容问答详解", use_container_width=True)
        st.markdown(
            """<div class='content'>
                步骤一：根据前文的网页分析，ai自动提取相应的文本概括描述信息，同时在网页内容详解处，根据上传网页信息给出用户对应的提示词提问信息。<br>
                步骤二：点击“提问”按钮，系统将自动调用模型进行回答，返回网页内容相关的答案。<br>
            </div>""",
            unsafe_allow_html=True
        )

    elif st.session_state.sub_page == "示例运行":
        st.markdown("<div class='title'>四、示例运行</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='content'>
                下面是一个完整的网页爬取流程示例：
            </div>
            """,
            unsafe_allow_html=True
        )
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '25.png'))
        st.image(image_path, caption="网页爬取示例", use_container_width=True)
        st.markdown(
            """<div class='content'>
                示例一：输入一个新闻网站的URL（如 https://news.example.com/article123）。
                对网页进行爬取后，得到该网页，网页标题，并生成AI摘要、Meta描述、关键词相关信息，并在下拉框中给出有关主要标题和ai摘要的内容预览，同时结合文档内容，给出相关资讯链接
            </div>""",
            unsafe_allow_html=True
        )
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '26.png'))
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '27.png'))
        st.image(image_path, caption="内容分析示例", use_container_width=True)
        st.markdown(
            """<div class='content'>
                示例二：点击“分析网页https://www.cnblogs.com/ymf123/p/5043510.html”后，系统返回问题和回答，并在下面给出详细分析：<br>
                - 包括对网页信息的一些重要信息，按照一定格式，显示在页面。在下面通过按钮点击展示更多的分析内容，比如“链接资源、源码预览、网页结构等内容”
            </div>""",
            unsafe_allow_html=True
        )

# 数据分析页面内容
elif st.session_state.current_page == "数据分析":
    st.title('欢迎来到小智数据分析')

    if st.session_state.sub_page == "分析介绍":
        st.markdown("<div class='title'>数据分析介绍</div><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="content">
                小智数据分析是一款强大的数据分析工具，能够处理各种类型的数据并生成有价值的见解。
                主要功能包括：
                - 数据清洗：处理缺失值、异常值等
                - 统计分析：计算各种统计指标
                - 数据可视化：生成图表和图形
                - 预测分析：基于历史数据进行预测
                - 文本分析：处理和分析文本数据
            </div>
        """, unsafe_allow_html=True)

# 数据可视化页面内容
elif st.session_state.current_page == "数据可视化":
    st.title('欢迎来到数据可视化')

    if st.session_state.sub_page == "可视化介绍":
        st.markdown("<div class='title'>一、数据可视化模块介绍</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="content">
                <strong>数据可视化助手</strong><br>
                是一款基于大语言模型与数据分析技术构建的智能数据可视化工具，支持用户上传数据文件并自动生成各类图表，进行趋势分析和特征检测。该工具可广泛应用于：<br>
                - 销售数据分析：展示销售额变化趋势、产品占比等<br>
                - 财务报表分析：生成资产负债表、利润表等可视化报告<br>
                - 科研数据分析：绘制实验结果的趋势图、分布图等<br>
                - 政府统计分析：制作人口、经济等指标的可视化图表<br>
                <strong>功能亮点：</strong><br>
                - 支持多种数据格式（Excel/CSV）<br>
                - 自动推荐合适的图表类型<br>
                - 提供详细的图形分析说明<br>
                - 支持交互式图表展示<br>
                - 可生成标准化JSON格式输出<br>
            </div>
            """,
            unsafe_allow_html=True
        )


    # 辅助函数：显示内容块

    def display_content(title, content, image_path=None, caption=None):
        st.markdown(f"<h2 class='title'>{title}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='content'>{content}</div>", unsafe_allow_html=True)
        if image_path:
            try:
                if os.path.exists(image_path):
                    st.image(image_path, caption=caption, use_container_width=True)
                else:
                    st.warning(f"图片未找到: {image_path}")
            except Exception as e:
                st.error(f"加载图片时出错: {str(e)}")

    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(project_root, '..', 'images')
    if st.session_state.sub_page == "使用指南":
        content = """
        根据提示词指南.txt中的原则，使用本数据可视化模块时建议遵循以下最佳实践：
        <strong>1. 明确需求：</strong><br>
           - 指定要展示的内容："请生成销售额的月度变化趋势"<br>
           - 说明目标受众："图表用于给管理层汇报"<br>
           - 描述特殊要求："突出显示异常值"<br>
        <strong>2. 构造提示词：</strong><br>
           - 使用三个引号分隔指令和上下文<br>
           - 具体描述需要生成的图表特征<br>
             - 类型："请生成一个柱状图"<br>
             - 时间范围："显示最近一年的数据"<br>
             - 关注指标："突出显示销售额和利润率"<br>
        <strong>3. 示例驱动：</strong><br>
           - 提供期望的输出格式示例<br>
           - 说明不需要包含的内容<br>
           - 指定分析深度和详细程度<br>
        <strong>4. 多轮迭代优化：</strong><br>
           - 初始请求后根据结果进行调整<br>
           - 逐步细化需求直到满意<br>
           - 利用对话记忆保持上下文连贯<br>
        """
        image_path = os.path.join(images_dir, '28.png')
        display_content(
            "二、使用指南",
            content,
            image_path,
            "数据可视化主界面示意图"
        )
        st.markdown("""
        <div class="content">
            数据可视化主界面布局。页面分为左右两列，左侧是侧边栏，可查看相应的历史对话，右侧为执行数据可视化的主要页面。<br>
            右侧分为上下结构，最上面可以查看一个简要的能力ai能力介绍和提问的提示词指南，用户选择上传文件类型（'xlsx'或者’csv',如果是'xlsx'文件，则选择单元表，执行分析，查看生成的图表和分析结果。
        </div>
        """, unsafe_allow_html=True)


    elif st.session_state.sub_page == "操作步骤":
        content = """
        下面是使用数据可视化模块的具体操作步骤：
        <strong>1. 准备数据</strong><br>
           - 上传要可视化的数据文件（Excel或CSV格式）<br>
           - 确认数据范围和字段含义<br>
           - 进行必要的数据清洗<br>
        <strong>2. 明确需求</strong><br>
           - 告知以下信息：<br>
            - 数据类型（时间序列、分类数据等）<br>
             - 展示目的（趋势分析、对比分析等）<br>
             - 目标受众（管理层、技术人员等）<br>
        <strong>3. 生成图表</strong><br>
           - 系统将：
           - 自动分析数据特征<br>
             - 推荐合适的图表类型<br>
             - 生成初步的可视化效果<br>
             - 提供详细的数据分析说明<br>
        <strong>4. 优化调整</strong><br>
        您可以要求：
             - 调整颜色方案和样式<br>
             - 修改图表大小和布局<br>
             - 添加或修改数据标签<br>
             - 导出图表为不同格式<br>
        """
        image_path = os.path.join(images_dir, '29.png')
        display_content(
            "三、操作步骤",
            content,
            image_path,
            "数据可视化步骤详解"
        )
        st.markdown("""
        <div class="content">
            步骤一：选择不同的模型版本，并启用对话记忆功能以保持上下文连贯。<br>
            步骤二：上传Excel或CSV格式的数据文件，系统会自动加载并显示前几行数据。<br>
            步骤三：在提问框内输入您的需求，点击“🚀 开始分析”按钮，系统将调用模型接口进行分析，并实时显示结果。
        </div>

        """, unsafe_allow_html=True)

    elif st.session_state.sub_page == "示例运行":
        st.markdown("<div class='title'>四、示例运行</div><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="content">
                下面是一个完整的数据可视化流程示例：

                示例一：上传一份销售数据Excel文件，包括产品名称、销售额、利润率等字段。
                在提问框中输入："这是近一年的销售数据，请展示各产品的销售额占比，图表用来给管理层汇报"。
                点击“🚀 开始分析”后，系统将：
                 - 自动识别数据特征
                 - 推荐饼图作为展示方式
                 - 生成可视化图表
                 - 提供详细的数据分析说明
            </div>
            """,
            unsafe_allow_html=True
        )
        # 添加图片
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', '30.png'))
        st.image(image_path, caption="数据可视化示例", use_container_width=True)
        st.markdown(
            """<div class="content">
                示例运行：用户上传销售数据文件，输入明确的需求描述，系统自动生成图像并提供详细的分析说明。
            </div>""",
            unsafe_allow_html=True
        )

