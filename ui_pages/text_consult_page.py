# 【修复版】智能文字问诊页面（解决所有报错+适配新用户逻辑）
import streamlit as st
import os
from config.paths import UPLOADS_DIR
from ai_core import get_text_diagnosis_result, speech_to_text, get_triage_result
from data import save_record
from utils import get_safe_time_str, generate_standard_medical_pdf
from config.settings import COMPLIANCE_FOOTER


def render_text_consult_page():
    st.subheader("💬 智能文字问诊")
    # ========== 【关键修复1】正确获取当前登录用户信息 ==========
    current_user = st.session_state.user_info
    user_id = current_user['user_id']
    default_realname = current_user['real_name']

    # 会话状态初始化
    if "diagnosis_result" not in st.session_state:
        st.session_state.diagnosis_result = None
    if "triage_result" not in st.session_state:
        st.session_state.triage_result = None
    if "final_record" not in st.session_state:
        st.session_state.final_record = None

    # 卡片样式的表单
    with st.container():
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        # ========== 【关键修复2】表单key唯一+必须有提交按钮 ==========
        with st.form("text_diagnosis_form", clear_on_submit=False):
            st.markdown("##### 一、患者基础信息")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("真实姓名", value=default_realname)
                age = st.number_input("年龄", min_value=1, max_value=120, key="text_age")
            with col2:
                gender = st.selectbox("性别", ["男", "女", "其他"], key="text_gender")
                medical_history = st.text_input("既往病史/过敏史（选填）", key="text_history")

            st.markdown("##### 二、症状描述")
            chief_complaint = st.text_input("【主诉】主要哪里不舒服？", placeholder="例：喉咙痛、咳嗽、发烧")
            onset_time = st.text_input("【发病时间】不舒服多久了？", placeholder="例：2天、1周")
            pain_level = st.selectbox("【疼痛程度】", ["无疼痛", "轻微", "中等", "严重", "无法忍受"])
            accompany_symptom = st.text_input("【伴随症状】有没有其他不舒服？", placeholder="例：轻微咳嗽、无发烧")
            inducement = st.text_input("【诱因】有没有什么原因导致的？", placeholder="例：着凉、吃了辛辣食物")
            treatment = st.text_input("【已做处理】有没有吃过药/做过检查？", placeholder="例：没吃药、喝了温水")
            extra_desc = st.text_area("【补充描述】还有其他需要说明的情况", height=80)

            # 语音输入
            audio_file = st.file_uploader("🎤 语音补充描述（可选）", type=["wav", "mp3", "m4a"], key="text_audio")
            audio_text = ""
            if audio_file:
                safe_time = get_safe_time_str()
                audio_path = os.path.join(UPLOADS_DIR, f"{safe_time}.wav")
                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                with st.spinner("正在识别语音..."):
                    try:
                        audio_text = speech_to_text(audio_path)
                        st.success(f"语音识别结果：{audio_text}")
                    except Exception as e:
                        st.error(f"语音识别失败：{str(e)}")

            # ========== 【关键修复3】表单必须有提交按钮 ==========
            submit_btn = st.form_submit_button("开始AI诊断分析", width="stretch", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    # 提交诊断逻辑
    if submit_btn:
        if not chief_complaint.strip() or not onset_time.strip():
            st.error("请至少填写【主诉】和【发病时间】，保证诊断准确")
        else:
            # 拼接完整的症状描述
            full_symptom = f"""
            主诉：{chief_complaint}
            发病时间：{onset_time}
            疼痛程度：{pain_level}
            伴随症状：{accompany_symptom if accompany_symptom else "无"}
            诱因：{inducement if inducement else "无"}
            已做处理：{treatment if treatment else "无"}
            补充描述：{extra_desc if extra_desc else "无"}
            语音补充：{audio_text if audio_text else "无"}
            """
            patient_info = {
                "name": name.strip(),
                "age": age,
                "gender": gender,
                "medical_history": medical_history
            }

            with st.spinner("AI正在分析您的情况，生成诊断报告..."):
                try:
                    # 生成诊断结果
                    diagnosis_result = get_text_diagnosis_result(patient_info, full_symptom)
                    diagnosis_result += COMPLIANCE_FOOTER
                    st.session_state.diagnosis_result = diagnosis_result

                    # 生成分诊结果
                    triage_result = get_triage_result(patient_info, full_symptom, diagnosis_result)
                    st.session_state.triage_result = triage_result

                    # 保存病历记录（绑定user_id）
                    safe_time = get_safe_time_str()
                    record = {
                        "time": safe_time,
                        "type": "文字问诊",
                        "user_id": user_id,
                        **patient_info,
                        "input": full_symptom,
                        "output": diagnosis_result
                    }
                    st.session_state.final_record = record
                    save_record(record)
                    st.toast("✅ 诊断完成，记录已自动保存至病历本")
                except Exception as e:
                    st.error(f"诊断出错：{str(e)}")

    # 展示诊断结果
    if st.session_state.final_record is not None:
        st.divider()
        
        # 诊断结果卡片
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### 🩺 AI辅助诊断结果")
        st.markdown(st.session_state.diagnosis_result)
        st.markdown('</div>', unsafe_allow_html=True)

        # 分诊结果
        if st.session_state.triage_result:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            triage = st.session_state.triage_result
            risk_color = {
                "低风险": "green",
                "中风险": "orange",
                "高风险": "red"
            }[triage['risk_level']]

            st.markdown("### 🏥 分诊结果")
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

        # 导出PDF按钮
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        pdf_buffer = generate_standard_medical_pdf(
            st.session_state.final_record,
            st.session_state.triage_result
        )
        st.download_button(
            label="📥 导出标准化医学报告PDF",
            data=pdf_buffer,
            file_name=f"{st.session_state.final_record['time']}_问诊报告.pdf",
            mime="application/pdf",
            width="stretch"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 补充提问功能
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### ❓ 补充提问")
        extra_question = st.text_input("还有其他问题，可以在这里提问")
        if st.button("发送提问", width="stretch") and extra_question.strip():
            with st.spinner("正在回复..."):
                from dashscope import Generation
                from config.settings import TEXT_MODEL
                prompt = f"""
                你是专业的临床医生，基于之前的诊断报告，回答患者的补充问题。
                患者信息：{st.session_state.final_record['name']}，{st.session_state.final_record['age']}岁
                之前的诊断结果：{st.session_state.diagnosis_result}
                患者的补充问题：{extra_question}
                要求：
                1. 回答严谨、简洁，仅做健康科普辅助
                2. 必须在末尾加上合规声明：本回答仅为健康科普参考，不替代执业医师面诊，身体不适请及时就医
                3. 禁止推荐处方药，禁止给出明确的治疗方案
                """
                response = Generation.call(
                    model=TEXT_MODEL,
                    prompt=prompt,
                    temperature=0.3,
                    max_tokens=500
                )
                if response.status_code == 200:
                    st.chat_message("assistant").write(response.output.text)
                else:
                    st.error("回复失败，请重试")
        st.markdown('</div>', unsafe_allow_html=True)

    # 重置按钮
    st.sidebar.divider()
    if st.sidebar.button("🔄 重置问诊页面", width="stretch", type="secondary"):
        for key in ["diagnosis_result", "triage_result", "final_record"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()