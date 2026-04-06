# 病历本页面（彻底修复导入报错+看不到记录问题）
import streamlit as st
import os
# 【关键修复】补全所有需要的函数导入
from data import load_all_records, filter_records, get_all_patient_names, get_all_record_types
from utils import generate_standard_medical_pdf
from utils.time_utils import parse_time_str
import datetime


def render_medical_record_page():
    """渲染病历管理页面，带权限控制和调试信息"""
    # 获取当前登录用户信息（强制标准化）
    current_user = st.session_state.user_info
    is_admin = (current_user['role'] == "admin")
    current_username = current_user['username'].strip().lower()

    st.subheader("📋 病历管理系统")
    if is_admin:
        st.caption("管理员权限：可查看所有患者的病历记录")
    else:
        st.caption(f"当前登录用户：{current_username}，仅可查看您本人的病历记录")

    # ========== 调试信息（帮助定位问题，可后续删除） ==========
    with st.expander("🔧 调试信息（看不到记录点这里）", expanded=False):
        st.write(f"当前登录用户名（标准化后）：`{current_username}`")
        all_records_debug = load_all_records()
        all_names_debug = list(set([r['name'] for r in all_records_debug]))
        st.write(f"系统中所有记录的姓名列表：{all_names_debug}")
        my_records_debug = [r for r in all_records_debug if r['name'] == current_username]
        st.write(f"匹配到您的记录数量：{len(my_records_debug)}")

    # 加载所有记录
    all_records = load_all_records()

    # ========== 权限过滤：双重校验，100%过滤 ==========
    if not is_admin:
        all_records = filter_records(all_records, user_id=current_user['user_id'])
        if len(all_records) == 0:
            st.warning(f"您（{current_user['real_name']}）暂无问诊记录，请先完成问诊")
            return

    # ========== 筛选区 ==========
    st.markdown("##### 🔍 记录筛选")
    if is_admin:
        # 管理员：3个筛选器
        filter_col1, filter_col2, filter_col3 = st.columns(3)

        # 1. 按患者姓名筛选
        all_names = get_all_patient_names(all_records)
        with filter_col1:
            selected_name = st.selectbox("选择患者", options=["全部患者"] + all_names, key="admin_user_name")

        # 2. 按诊断类型筛选
        all_types = get_all_record_types(all_records)
        with filter_col2:
            selected_type = st.selectbox("诊断类型", options=["全部类型"] + all_types, key="admin_record_type")

        # 3. 按时间范围筛选
        min_date = parse_time_str(all_records[-1]['time']) if all_records else datetime.datetime.today().date()
        max_date = datetime.datetime.today().date()
        with filter_col3:
            date_range = st.date_input(
                "问诊时间范围",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                format="YYYY-MM-DD",
                key="admin_date_range"
            )

        # 执行筛选
        filtered_records = filter_records(all_records, name=selected_name, record_type=selected_type,
                                          date_range=date_range)
    else:
        # 普通用户：仅保留类型和时间筛选
        filter_col1, filter_col2 = st.columns(2)

        # 1. 按诊断类型筛选
        all_types = get_all_record_types(all_records)
        with filter_col1:
            selected_type = st.selectbox("诊断类型", options=["全部类型"] + all_types, key="user_record_type")

        # 2. 按时间范围筛选
        min_date = parse_time_str(all_records[-1]['time']) if all_records else datetime.datetime.today().date()
        max_date = datetime.datetime.today().date()
        with filter_col2:
            date_range = st.date_input(
                "问诊时间范围",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                format="YYYY-MM-DD",
                key="user_date_range"
            )

        # 执行筛选（固定姓名为当前用户）
        filtered_records = filter_records(all_records, record_type=selected_type,
                                          date_range=date_range)
# ... existing code ...

    # 筛选结果统计
    st.divider()
    st.markdown(f"**筛选结果：共找到 {len(filtered_records)} 条记录**")
    st.divider()

    # ========== 记录展示 ==========
    if is_admin:
        # 管理员：按患者分组展示
        name_group = {}
        for record in filtered_records:
            patient_name = record['name'].strip().lower()
            if patient_name not in name_group:
                name_group[patient_name] = []
            name_group[patient_name].append(record)

        # 逐个患者展示
        for patient_name, records in name_group.items():
            with st.expander(f"👤 患者：{patient_name}（共 {len(records)} 条记录）", expanded=False):
                for record in records:
                    with st.container(border=True):
                        st.markdown(f"**📅 问诊时间：** {record['time']}  **🏷️ 诊断类型：** {record['type']}")
                        st.write(f"**患者信息：** {record['name']}，{record['age']}岁，{record['gender']}")

                        if record['input'].strip():
                            with st.expander("查看症状描述", expanded=False):
                                st.write(record['input'])

                        if record['image_path'] and os.path.exists(record['image_path']):
                            with st.expander("查看病灶图片", expanded=False):
                                st.image(record['image_path'], width=300)

                        with st.expander("查看AI诊断详情", expanded=False):
                            st.markdown(record['output'])

                        # 导出PDF按钮
                        pdf_buffer = generate_standard_medical_pdf(record)
                        st.download_button(
                            label="📥 导出该记录PDF报告",
                            data=pdf_buffer,
                            file_name=f"{record['time']}_{record['type']}_报告.pdf",
                            mime="application/pdf",
                            key=f"admin_download_{record['file_name']}"
                        )
    else:
        # 普通用户：直接展示自己的所有记录
        for record in filtered_records:
            with st.container(border=True):
                st.markdown(f"**📅 问诊时间：** {record['time']}  **🏷️ 诊断类型：** {record['type']}")
                st.write(f"**患者信息：** {record['name']}，{record['age']}岁，{record['gender']}")

                if record['input'].strip():
                    with st.expander("查看症状描述", expanded=False):
                        st.write(record['input'])

                if record['image_path'] and os.path.exists(record['image_path']):
                    with st.expander("查看病灶图片", expanded=False):
                        st.image(record['image_path'], width=300)

                with st.expander("查看AI诊断详情", expanded=False):
                    st.markdown(record['output'])

                # 导出PDF按钮
                pdf_buffer = generate_standard_medical_pdf(record)
                st.download_button(
                    label="📥 导出该记录PDF报告",
                    data=pdf_buffer,
                    file_name=f"{record['time']}_{record['type']}_报告.pdf",
                    mime="application/pdf",
                    key=f"user_download_{record['file_name']}"
                )