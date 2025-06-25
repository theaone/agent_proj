import streamlit as st
import requests
import cv2
import numpy as np
from io import BytesIO
import base64

# 页面配置
st.set_page_config(
    page_title="图像处理助手",
    page_icon="🖼️",
    layout="wide"
)

# 初始化会话状态
if "image_analysis" not in st.session_state:
    st.session_state.image_analysis = ""

if "image_annotations" not in st.session_state:
    st.session_state.image_annotations = []

if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False


def is_valid_image(file):
    """检查是否是有效的图像文件"""
    try:
        file.seek(0)
        data = file.read(1024)
        if not data:
            return False
        file.seek(0)
        return True
    except Exception:
        return False


def load_image_cv2(file):
    """
    使用 OpenCV 加载图像以提高兼容性
    :param file: Streamlit 上传的文件对象
    :return: RGB 格式的 NumPy 图像数组 或 None
    """
    try:
        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("OpenCV 无法解码图像，请检查文件有效性")
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 转换为 RGB 显示
    except Exception as e:
        st.error(f"图像加载失败：{str(e)}")
        return None


# 主函数
def main():
    st.title("图像处理助手 🖼️")
    st.markdown("上传图像并进行智能分析，识别物体、场景、人物等元素，并进行分类和标注。")

    # 侧边栏配置
    with st.sidebar.expander("🔧 模型配置", expanded=True):
        api_base = st.text_input(
            "API 地址",
            value="https://open.bigmodel.cn/api/paas/v4/",
            placeholder="输入大模型API地址"
        )
        api_key = st.text_input(
            "API 密钥",
            value="fdfb212b7d3249b587db02ffe470688e.X6K9sEMw0hCzlJNd",
            type="password",
            placeholder="输入你的API密钥"
        )
        model_name = st.selectbox(
            "模型选择",
            ["glm-4v", "gpt-4-vision"]
        )
        temperature = st.slider(
            "生成温度",
            min_value=0.0, max_value=1.0, value=0.1,
            help="控制输出的随机性，较低值更确定性"
        )

        # 调试选项
        st.subheader("🔧 调试选项")
        st.session_state.debug_mode = st.checkbox("启用调试模式", False)
        if st.session_state.debug_mode:
            st.warning("调试模式会显示详细的 API 响应信息，可能包含敏感数据")

    # 图像上传区域
    with st.expander("📁 上传图像进行分析", expanded=True):
        uploaded_image = st.file_uploader(
            "支持 .jpg, .png, .jpeg 格式",
            type=["jpg", "png", "jpeg"]
        )

        if uploaded_image:
            if not is_valid_image(uploaded_image):
                st.error("上传的文件不是有效的图像，请重新上传")
                return

            # 使用 OpenCV 加载图像
            image = load_image_cv2(uploaded_image)

            if image is not None:
                st.image(image, caption="上传的图像", use_column_width=True)

                # 将图像转换为 base64 字符串用于 API 请求
                _, img_encoded = cv2.imencode(".jpg", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                img_bytes = img_encoded.tobytes()
                encoded_img = base64.b64encode(img_bytes).decode('utf-8')

                # 分析图像按钮
                if st.button("🔍 开始分析图像"):
                    with st.spinner("正在分析图像内容..."):
                        payload = {
                            "model": model_name,
                            "temperature": temperature,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": "请详细描述这张图像中的内容，包括物体、场景、人物等元素，并进行分类和标注。"},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_img}"}}
                                    ]
                                }
                            ]
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

                            if "choices" in response and len(response["choices"]) > 0:
                                analysis_result = response["choices"][0]["message"]["content"].strip()
                                st.session_state.image_analysis = analysis_result
                                st.success("图像分析完成！可以查看结果或继续提问")

                                # 模拟标注（实际应用中可调用计算机视觉模型）
                                st.session_state.image_annotations = [
                                    {"label": "人", "confidence": 0.92},
                                    {"label": "汽车", "confidence": 0.85},
                                    {"label": "建筑物", "confidence": 0.90}
                                ]

                            else:
                                st.error(f"无法解析响应格式: {response}")

                        except Exception as e:
                            st.error(f"图像分析失败: {str(e)}")

    if st.session_state.image_analysis:
        st.subheader("📊 图像分析结果")
        st.markdown(st.session_state.image_analysis)

        # 显示并导出结构化标注信息
        if st.session_state.image_annotations:
            # 分类整理标注信息
            structured_annotations = {
                "人物信息": [],
                "车辆信息": [],
                "建筑物信息": [],
                "其他信息": []
            }

            for annotation in st.session_state.image_annotations:
                label = annotation["label"]
                confidence = annotation["confidence"]
                item = {"名称": label, "置信度": confidence}

                if "人" in label or "人物" in label:
                    structured_annotations["人物信息"].append(item)
                elif "车" in label or "汽车" in label or "车辆" in label:
                    structured_annotations["车辆信息"].append(item)
                elif "建筑" in label or "楼" in label or "房屋" in label:
                    structured_annotations["建筑物信息"].append(item)
                else:
                    structured_annotations["其他信息"].append(item)

            # 展示结构化信息
            st.subheader("📌 结构化标注信息")

            for category, items in structured_annotations.items():
                if items:
                    st.markdown(f"**{category}**")
                    for item in items:
                        st.markdown(f"- {item['名称']} (置信度: {int(item['置信度'] * 100)}%)")

            # 导出为JSON
            import json

            def generate_json():
                return json.dumps(structured_annotations, indent=4, ensure_ascii=False)

            json_data = generate_json()

            st.download_button(
                label="📥 下载结构化标注结果为JSON",
                data=json_data,
                file_name="structured_image_annotations.json",
                mime="application/json",
                key="structured_download_json_button"  # 增加唯一 key 避免重复ID冲突
            )

        # 底部信息
        st.markdown("---")
        st.markdown("© 2025 图像处理助手 | 使用大语言模型与计算机视觉技术构建")


if __name__ == "__main__":
    main()