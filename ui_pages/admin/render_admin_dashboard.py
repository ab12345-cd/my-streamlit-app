# 管理员数据看板页面
import streamlit as st
import pandas as pd
from data import get_all_users, load_all_records
from utils.time_utils import parse_time_str


def render_admin_dashboard():
    st.subheader("📊 系统管理看板")

    # 核心数据统计
    all_users = get_all_users()
    all_records = load_all_records()
    total_users = len(all_users)
    total_records = len(all_records)
    admin_users = len([u for u in all_users if u['role'] == "admin"])
    normal_users = total_users - admin_users

    # 数据卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总用户数", total_users)
    with col2:
        st.metric("普通用户数", normal_users)
    with col3:
        st.metric("总问诊记录数", total_records)
    with col4:
        st.metric("管理员数", admin_users)

    st.divider()
    # 问诊类型分布
    st.markdown("##### 📈 问诊类型分布")
    if all_records:
        type_df = pd.DataFrame(all_records)
        type_count = type_df['type'].value_counts()
        st.bar_chart(type_count)
    else:
        st.info("暂无问诊记录")

    st.divider()
    # 风险等级分布
    st.markdown("##### ⚠ 风险等级分布")
    if all_records:
        # 提取风险等级
        risk_list = []
        for record in all_records:
            if 'triage_result' in record and record['triage_result']:
                risk_list.append(record['triage_result'].get('risk_level', '未知'))
        if risk_list:
            risk_df = pd.Series(risk_list).value_counts()
            st.bar_chart(risk_df, color="#ff4b4b")
        else:
            st.info("暂无分诊风险数据")
    else:
        st.info("暂无问诊记录")

    st.divider()
    # 最近10条问诊记录
    st.markdown("##### 📋 最近10条问诊记录")
    if all_records:
        # 按时间倒序
        all_records_sorted = sorted(all_records, key=lambda x: parse_time_str(x['time']), reverse=True)
        recent_records = all_records_sorted[:10]
        # 转成表格
        recent_df = pd.DataFrame([{
            "问诊时间": r['time'],
            "患者姓名": r['name'],
            "诊断类型": r['type'],
            "用户ID": r['user_id']
        } for r in recent_records])
        st.dataframe(recent_df, width="stretch")
    else:
        st.info("暂无问诊记录")