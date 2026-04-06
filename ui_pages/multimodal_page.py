# 【修复版】多模态联合诊断页面（解决所有报错+适配新用户逻辑）
import streamlit as st
import os
from PIL import Image
from config.paths import UPLOADS_DIR
from ai_core import get_multimodal_diagnosis_result, get_lesion_annotation, get_triage_result
from data import save_record
from utils import get_safe_time_str, generate_standard_medical_pdf
from config.settings import COMPLIANCE_FOOTER


def render_multimodal_page():
    st.subheader("🤝 多模态联合诊断（文字+图片综合分析）")
    st.caption("同时上传病灶图片+描述症状，AI会结合两者给出更精准的辅助分析，这是本项目的核心创新点")
    # ========== 【关键修复1】正确获取当前登录用户信息 ==========
    current_user = st.session_state.user_info
    user_id = current_user['user_id']
    default_realname = current_user['real_name']

    # 会话状态初始化
    if "mm_result" not in st.session_state:
        st.session_state.mm_result = None
    if "annotated_image" not in st.session_state:
        st.session_state.annotated_image = None
    if "lesion_data" not in st.session_state:
        st.session_state.lesion_data = []
    if "mm_triage" not in st.session_state:
        st.session_state.mm_triage = None
    if "mm_record" not in st.session_state:
        st.session_state.mm_record = None

    # ========== 【关键修复2】表单key唯一+必须有提交按钮 ==========
    with st.form("multimodal_diagnosis_form", clear_on_submit=False):
        st.markdown("##### 患者基础信息")
        col1, col2 = st.columns(2)
        with col1:
            mm_name = st.text_input("患者姓名", value=default_realname)
            mm_age = st.number_input("年龄", min_value=1, max_value=120, key="mm_age")
        with col2:
            mm_gender = st.selectbox("性别", ["男", "女", "其他"], key="mm_gender")
            mm_history = st.text_input("既往病史/过敏史（选填）", key="mm_history")

        st.markdown("##### 症状与图片上传")
        symptom_desc = st.text_area("详细描述你的症状、发病时间、不适感等", height=100, key="mm_symptom")
        mm_uploaded_file = st.file_uploader("上传对应的病灶图片", type=["jpg", "jpeg", "png"], key="mm_img")

        # ========== 【关键修复3】表单必须有提交按钮 ==========
        submit_mm = st.form_submit_button("开始多模态综合分析", width="stretch", type="primary")

    # 提交逻辑
    if submit_mm:
        if not symptom_desc.strip():
            st.warning("请详细描述症状")
        elif mm_uploaded_file is None:
            st.warning("请上传对应的病灶图片")
        else:
            # 保存图片
            mm_image = Image.open(mm_uploaded_file).convert("RGB")
            safe_time = get_safe_time_str()
            mm_img_path = os.path.join(UPLOADS_DIR, f"{safe_time}_多模态.png")
            mm_image.save(mm_img_path)
            mm_img_abs_path = os.path.abspath(mm_img_path)

            with st.spinner("AI正在综合分析文字与图片信息..."):
                try:
                    # 1. 病灶标注
                    try:
                        annotated_image, lesion_list = get_lesion_annotation(mm_img_abs_path)
                        st.session_state.annotated_image = annotated_image
                        st.session_state.lesion_data = lesion_list
                        if len(lesion_list) == 0:
                            st.info("未识别到明显异常病灶，诊断分析已完成")
                        else:
                            st.success(f"成功识别到{len(lesion_list)}个病灶，诊断分析已完成")
                    except Exception as e:
                        st.warning(f"病灶可视化标注失败：{str(e)}，将跳过标注继续诊断")
                        st.session_state.annotated_image = mm_image
                        st.session_state.lesion_data = []

                    # 2. 综合诊断
                    patient_info = {
                        "name": mm_name.strip(),
                        "age": mm_age,
                        "gender": mm_gender,
                        "medical_history": mm_history
                    }
                    result_text = get_multimodal_diagnosis_result(patient_info, symptom_desc, mm_img_abs_path)
                    result_text += COMPLIANCE_FOOTER
                    st.session_state.mm_result = result_text

                    # 3. 分诊
                    triage_result = get_triage_result(patient_info, symptom_desc, result_text)
                    st.session_state.mm_triage = triage_result

                    # 4. 保存记录（绑定user_id）
                    record = {
                        "time": safe_time,
                        "type": "多模态联合诊断",
                        "user_id": user_id,
                        **patient_info,
                        "input": symptom_desc,
                        "image_path": mm_img_path,
                        "output": result_text,
                        "lesions": st.session_state.lesion_data
                    }
                    st.session_state.mm_record = record
                    save_record(record)
                    st.toast("✅ 多模态诊断记录已保存")
                except Exception as e:
                    st.error(f"分析出错：{str(e)}")

    # 展示结果
    if st.session_state.mm_record is not None:
        st.divider()
        st.markdown("##### 🔍 病灶可视化分析")
        col1, col2 = st.columns(2)
        with col1:
            st.image(Image.open(st.session_state.mm_record['image_path']), caption="原图", width="stretch")
        with col2:
            st.image(st.session_state.annotated_image, caption="AI病灶标注", width="stretch")

        # 病灶数据
        if st.session_state.lesion_data:
            st.markdown("##### 📊 病灶特征数据")
            st.dataframe(st.session_state.lesion_data, width="stretch")

        # 诊断结果
        st.divider()
        st.markdown("##### 🩺 综合诊断分析结果")
        st.markdown(st.session_state.mm_result)

        # 分诊结果
        if st.session_state.mm_triage:
            st.divider()
            triage = st.session_state.mm_triage
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

        # 导出PDF
        st.divider()
        pdf_buffer = generate_standard_medical_pdf(
            st.session_state.mm_record,
            st.session_state.mm_triage
        )
        st.download_button(
            label="📥 导出标准化医学报告PDF",
            data=pdf_buffer,
            file_name=f"{st.session_state.mm_record['time']}_多模态诊断报告.pdf",
            mime="application/pdf",
            width="stretch"
        )

    # 重置按钮
    st.sidebar.divider()
    if st.sidebar.button("🔄 重置页面", width="stretch", type="secondary"):
        for key in ["mm_result", "annotated_image", "lesion_data", "mm_triage", "mm_record"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()