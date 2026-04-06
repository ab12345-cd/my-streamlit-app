import streamlit as st
from data import get_all_users, register_user


def render_user_manage():
    st.subheader("👤 用户管理")

    # 新增用户
    with st.expander("新增用户", expanded=False):
        with st.form("add_user_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            role = st.selectbox("角色", ["user", "admin"])
            submit = st.form_submit_button("新增用户", use_container_width=True)
        if submit:
            success, msg = register_user(username, password, role)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    # 用户列表
    st.divider()
    all_users = get_all_users()
    st.dataframe(all_users, use_container_width=True)