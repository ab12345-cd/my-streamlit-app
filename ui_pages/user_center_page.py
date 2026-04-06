# 个人中心页面（修复命名冲突）
import streamlit as st
from data import update_user_info, get_user_record_count

def render_user_center_page():
    st.subheader("👤 个人中心")
    current_user = st.session_state.user_info
    user_id = current_user['user_id']

    # 用户信息卡片
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("登录账号", current_user['username'])
            st.metric("用户角色", "管理员" if current_user['role'] == "admin" else "普通用户")
        with col2:
            st.metric("真实姓名", current_user['real_name'])
            st.metric("总问诊次数", get_user_record_count(user_id))

    st.divider()
    # 修改个人信息
    st.markdown("##### ✏️ 修改个人信息")
    with st.form("update_info_form"):
        new_realname = st.text_input("新的真实姓名", value=current_user['real_name'])
        new_password = st.text_input("新密码（不修改请留空）", type="password")
        confirm_password = st.text_input("确认新密码", type="password")
        submit_update = st.form_submit_button("确认修改", width="stretch")

    if submit_update:
        if new_password and new_password != confirm_password:
            st.error("两次输入的密码不一致")
        else:
            success, msg = update_user_info(user_id, new_realname, new_password if new_password else None)
            if success:
                # 更新session里的姓名
                st.session_state.user_info['real_name'] = new_realname.strip()
                st.success("修改成功！页面即将刷新...")
                st.rerun()
            else:
                st.error(msg)

    st.divider()
    # 账号安全提示
    st.info("⚠ 账号安全提示：请定期修改密码，不要使用弱密码；本系统仅用于健康辅助，请勿上传敏感隐私信息。")