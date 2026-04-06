import streamlit as st
from data import load_all_records, get_all_users


def render_admin_dashboard():
    st.subheader("📊 系统管理看板")

    all_records = load_all_records()
    all_users = get_all_users()

    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总用户数", len(all_users))
    with col2:
        st.metric("总问诊记录", len(all_records))
    with col3:
        st.metric("总患者数", len(set([r['name'] for r in all_records])))
    with col4:
        type_count = {}
        for r in all_records:
            type_count[r['type']] = type_count.get(r['type'], 0) + 1
        st.metric("最常用功能", max(type_count, key=type_count.get) if type_count else "无")

    # 趋势图
    st.divider()
    st.subheader("问诊记录趋势")
    date_count = {}
    for r in all_records:
        date = r['time'].split(' ')[0]
        date_count[date] = date_count.get(date, 0) + 1
    if date_count:
        st.bar_chart(date_count)
    else:
        st.info("暂无数据")