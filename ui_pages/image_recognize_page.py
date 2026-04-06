# 【修复版】病灶图片识别页面（解决所有报错+适配新用户逻辑）
import streamlit as st
import os
from PIL import Image
from config.paths import UPLOADS_DIR
from ai_core import get_image_recognition_result, get_lesion_annotation, get_triage_result
from data import save_record
from utils import get_safe_time_str, generate_standard_medical_pdf
from config.settings import COMPLIANCE_FOOTER


def render_image_recognize_page():
    st.subheader("🖼️ 病灶图片识别与分析")
    st.caption("支持：皮肤疾病、口腔问题、眼部浅表病灶、外伤等浅表性病症识别")
    # ========== 【关键修复1】正确获取当前登录用户信息 ==========
    current_user = st.session_state.user_info
    user_id = current_user['user_id']
    default_realname = current_user['real_name']

    # 会话状态初始化
    if "img_result" not in st.session_state:
        st.session_state.img_result = None
    if "annotated_image" not in st.session_state:
        st.session_state.annotated_image = None
    if "lesion_data" not in st.session_state:
        st.session_state.lesion_data = []
    if "img_triage" not in st.session_state:
        st.session_state.img_triage = None
    if "img_record" not in st.session_state:
        st.session_state.img_record = None

    # 卡片样式的表单
    with st.container():
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        # ========== 【关键修复2】表单key唯一+必须有提交按钮 ==========
        with st.form("image_diagnosis_form", clear_on_submit=False):
            st.markdown("##### 患者基础信息")
            col1, col2 = st.columns(2)
            with col1:
                img_name = st.text_input("真实姓名", value=default_realname)
                img_age = st.number_input("年龄", min_value=1, max_value=120, key="img_age")
            with col2:
                img_gender = st.selectbox("性别", ["男", "女", "其他"], key="img_gender")
                img_history = st.text_input("既往病史/过敏史（选填）", key="img_history")

            st.markdown("##### 病灶图片上传")
            uploaded_file = st.file_uploader("请上传清晰的病灶照片", type=["jpg", "jpeg", "png"], key="img_upload")
            symptom_desc = st.text_area("补充症状描述（选填）", height=80, key="img_symptom",
                                        placeholder="请描述症状、发病时间、不适感等")

            # ========== 【关键修复3】表单必须有提交按钮 ==========
            submit_img = st.form_submit_button("开始AI识别分析", width="stretch", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    # 提交逻辑
    if submit_img:
        if uploaded_file is None:
            st.warning("请上传病灶图片")
        else:
            # 保存图片
            image = Image.open(uploaded_file).convert("RGB")
            safe_time = get_safe_time_str()
            img_path = os.path.join(UPLOADS_DIR, f"{safe_time}.png")
            image.save(img_path)
            img_abs_path = os.path.abspath(img_path)

            with st.spinner("AI正在识别病灶并分析..."):
                try:
                    # 1. 病灶标注
                    try:
                        annotated_image, lesion_list = get_lesion_annotation(img_abs_path)
                        st.session_state.annotated_image = annotated_image
                        st.session_state.lesion_data = lesion_list
                        if len(lesion_list) == 0:
                            st.info("未识别到明显异常病灶，诊断分析已完成")
                        else:
                            st.success(f"成功识别到{len(lesion_list)}个病灶，诊断分析已完成")
                    except Exception as e:
                        st.warning(f"病灶可视化标注失败：{str(e)}，将跳过标注，继续完成诊断")
                        st.session_state.annotated_image = image
                        st.session_state.lesion_data = []

                    # 2. 诊断分析
                    patient_info = {
                        "name": img_name.strip(),
                        "age": img_age,
                        "gender": img_gender,
                        "medical_history": img_history
                    }
                    diagnosis_result = get_image_recognition_result(patient_info, img_abs_path, symptom_desc)
                    diagnosis_result += COMPLIANCE_FOOTER
                    st.session_state.img_result = diagnosis_result

                    # 3. 分诊
                    full_symptom = f"图片识别，补充症状：{symptom_desc if symptom_desc else '无'}"
                    triage_result = get_triage_result(patient_info, full_symptom, diagnosis_result)
                    st.session_state.img_triage = triage_result

                    # 4. 保存记录（绑定user_id）
                    record = {
                        "time": safe_time,
                        "type": "图片识别",
                        "user_id": user_id,
                        **patient_info,
                        "image_path": img_path,
                        "input": full_symptom,
                        "output": diagnosis_result,
                        "lesions": st.session_state.lesion_data
                    }
                    st.session_state.img_record = record
                    save_record(record)
                    st.toast("✅ 识别记录已保存至病历本")
                except Exception as e:
                    st.error(f"分析出错：{str(e)}")

    # 展示结果
    if st.session_state.img_record is not None:
        st.divider()
        
        # 病灶可视化分析结果卡片
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("##### 🔍 病灶可视化分析结果")

        # 两图对比展示
        col1, col2 = st.columns(2)
        with col1:
            st.image(Image.open(st.session_state.img_record['image_path']), caption="原图", width="stretch")
        with col2:
            st.image(st.session_state.annotated_image, caption="AI病灶标注", width="stretch")

        # 病灶特征数据
        if st.session_state.lesion_data:
            st.markdown("##### 📊 病灶特征数据")
            st.dataframe(st.session_state.lesion_data, width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

        # 诊断结果卡片
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("##### 🩺 AI诊断分析结果")
        st.markdown(st.session_state.img_result)
        st.markdown('</div>', unsafe_allow_html=True)

        # 分诊结果卡片
        if st.session_state.img_triage:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            triage = st.session_state.img_triage
            risk_color = {
                "低风险": "green",
                "中风险": "orange",
                "高风险": "red"
            }[triage['risk_level']]

            st.markdown(f"##### 🏥 分诊结果")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("推荐就诊科室", triage['department'])
            with col2:
                st.metric("风险等级", f":{risk_color}[{triage['risk_level']}]")

            st.info(triage['risk_desc'])
            if triage['risk_level'] == "高风险":
                st.error(f"⚠ 紧急提醒：{triage['warning']}")
            else:
                st.warning(f"就诊提醒：{triage['warning']}")
            st.markdown('</div>', unsafe_allow_html=True)

        # 导出PDF卡片
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        pdf_buffer = generate_standard_medical_pdf(
            st.session_state.img_record,
            st.session_state.img_triage
        )
        st.download_button(
            label="📥 导出标准化医学报告PDF",
            data=pdf_buffer,
            file_name=f"{st.session_state.img_record['time']}_病灶识别报告.pdf",
            mime="application/pdf",
            width="stretch"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # 重置按钮
    st.sidebar.divider()
    if st.sidebar.button("🔄 重置页面", width="stretch", type="secondary"):
        for key in ["img_result", "annotated_image", "lesion_data", "img_triage", "img_record"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()