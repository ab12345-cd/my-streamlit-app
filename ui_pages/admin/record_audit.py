# 报告审核页面（修复导入报错）
import streamlit as st
from data import load_all_records, filter_records, get_all_patient_names, get_all_record_types
from utils import generate_standard_medical_pdf
import datetime


def render_record_audit():
    st.subheader("📑 报告审核管理")

    all_records = load_all_records()
    if not all_records:
        st.info("暂无记录")
        return

    # 筛选区（加唯一key，避免重复ID）
    st.markdown("##### 🔍 记录筛选")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    all_names = get_all_patient_names(all_records)
    with filter_col1:
        selected_name = st.selectbox("选择患者", options=["全部患者"] + all_names, key="audit_select_name")

    all_types = get_all_record_types(all_records)
    with filter_col2:
        selected_type = st.selectbox("诊断类型", options=["全部类型"] + all_types, key="audit_select_type")

    min_date = datetime.datetime.strptime(all_records[-1]['time'].split(' ')[0], "%Y-%m-%d").date()
    max_date = datetime.datetime.today().date()
    with filter_col3:
        date_range = st.date_input(
            "问诊时间范围",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            format="YYYY-MM-DD",
            key="audit_date_range"
        )

    # 执行筛选
    filtered_records = filter_records(all_records, selected_name, selected_type, date_range)
    st.markdown(f"**筛选结果：共找到 {len(filtered_records)} 条记录**")
    st.divider()

    # 记录列表
    for record in filtered_records:
        with st.container(border=True):
            st.markdown(f"**📅 问诊时间：** {record['time']}  **🏷️ 诊断类型：** {record['type']}")
            st.write(f"**患者信息：** {record['name']}，{record['age']}岁，{record['gender']}")

            col1, col2 = st.columns(2)
            with col1:
                with st.expander("查看详情", expanded=False):
                    if record['input'].strip():
                        st.write("**症状描述：**", record['input'])
                    st.markdown("**诊断结果：**")
                    st.markdown(record['output'])
            with col2:
                # 导出PDF，加唯一key
                pdf_buffer = generate_standard_medical_pdf(record)
                st.download_button(
                    label="📥 导出PDF报告",
                    data=pdf_buffer,
                    file_name=f"{record['time']}_{record['type']}_报告.pdf",
                    mime="application/pdf",
                    key=f"audit_download_{record['file_name']}"
                )