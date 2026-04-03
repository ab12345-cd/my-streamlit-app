# 项目主入口（重构：用户名与真实姓名分离）
# 项目主入口（重构：用户名与真实姓名分离）
# 强制设置全局编码为 utf-8，彻底解决 Windows 中文编码问题
import sys
import os
from importlib import reload

os.environ['PYTHONUTF8'] = '1'
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# ... existing code ...
# 【最终优化版】AI多模态医疗辅助问诊系统 主入口
import streamlit as st
from streamlit_option_menu import option_menu

# ========== 全局配置 ==========
st.set_page_config(
    page_title="AI多模态医疗辅助问诊系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "AI多模态医疗辅助问诊系统 - 计算机设计大赛参赛作品"
    }
)

# ========== 全局CSS（解决白杠突兀+统一风格） ==========
st.markdown("""
<style>
/* 全局背景 */
.stApp {
    background-color: #F5F7FA !important;
}
.main .block-container {
    background-color: #F5F7FA !important;
    padding: 1.5rem 3rem !important;
    max-width: 100% !important;
}

/* 全局主色调 */
:root {
    --primary-color: #165DFF;
    --primary-light: #E8F3FF;
    --text-primary: #1D2129;
    --text-secondary: #4E5969;
    --text-weak: #86909C;
    --card-bg: #FFFFFF;
    --border-color: #E5E6EB;
}

/* 全局字体统一 */
html, body, [class*="css"] {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif !important;
    color: var(--text-primary) !important;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
    margin: 0 0 0.8rem 0 !important;
}

/* 【核心优化】卡片样式：去掉突兀白杠，间距更紧凑 */
.medical-card {
    background: var(--card-bg) !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06) !important;
    padding: 1.2rem 1.5rem !important;
    margin: 0 0 1rem 0 !important;
    border: 1px solid var(--border-color) !important;
}

/* 按钮美化 */
.stButton>button {
    width: 100% !important;
    height: 42px !important;
    border-radius: 8px !important;
    background-color: var(--primary-color) !important;
    color: white !important;
    border: none !important;
    font-weight: 500 !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
}
.stButton>button:hover {
    background-color: #0E42D2 !important;
    box-shadow: 0 4px 12px 0 rgba(22, 93, 255, 0.3) !important;
}
.stButton>button:active {
    background-color: #0A34A8 !important;
}

/* 次要按钮 */
.secondary-btn>button {
    background-color: white !important;
    color: var(--primary-color) !important;
    border: 1px solid var(--primary-color) !important;
}
.secondary-btn>button:hover {
    background-color: var(--primary-light) !important;
    color: var(--primary-color) !important;
}

/* 表单输入框美化 */
.stTextInput>div>div>input, 
.stTextArea>div>div>textarea,
.stNumberInput>div>div>input,
.stSelectbox>div>div>div,
.stFileUploader>div>div,
.stDateInput>div>div>div {
    border-radius: 8px !important;
    border: 1px solid var(--border-color) !important;
    padding: 0.6rem 0.8rem !important;
    font-size: 14px !important;
    transition: all 0.3s ease !important;
}
.stTextInput>div>div>input:focus, 
.stTextArea>div>div>textarea:focus,
.stNumberInput>div>div>input:focus,
.stSelectbox>div>div>div:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 2px rgba(22, 93, 255, 0.2) !important;
}

/* 侧边栏样式 */
section[data-testid="stSidebar"] {
    background-color: var(--card-bg) !important;
    border-right: 1px solid var(--border-color) !important;
    padding-top: 1.5rem !important;
    min-width: 280px !important;
    max-width: 300px !important;
}
section[data-testid="stSidebar"] .sidebar-content {
    padding: 0 !important;
}

/* 保留侧边栏展开按钮，只隐藏右上角多余菜单 */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}
button[data-testid="stMainMenu"] {
    visibility: hidden !important;
}

/* 隐藏冗余元素 */
footer {visibility: hidden !important;}

/* 分割线样式 */
hr {
    border: none !important;
    border-top: 1px solid var(--border-color) !important;
    margin: 1.5rem 0 !important;
}

/* 风险等级颜色 */
.risk-low {color: #00B42A !important; font-weight: 600 !important;}
.risk-medium {color: #FF7D00 !important; font-weight: 600 !important;}
.risk-high {color: #F53F3F !important; font-weight: 600 !important;}

/* 表格美化 */
.stDataFrame {
    border-radius: 8px !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ========== 导入功能模块 ==========
from config.settings import COMPLIANCE_WARNING
from data import login_user, register_user, init_admin_user
from ui_pages import (
    render_multimodal_page,
    render_text_consult_page,
    render_image_recognize_page,
    render_medical_record_page,
    render_user_center_page
)
from ui_pages.admin import render_admin_dashboard, render_user_manage, render_record_audit

# 初始化管理员账号
init_admin_user()

# ========== 登录状态管理 ==========
if "login_status" not in st.session_state:
    st.session_state.login_status = False
    st.session_state.user_info = None

# 未登录：登录注册页面
if not st.session_state.login_status:
    st.markdown("<h1 style='text-align: center; margin: 2rem 0 3rem 0;'>🏥 AI多模态医疗辅助问诊系统</h1>",
                unsafe_allow_html=True)

    login_col, _, register_col = st.columns([4, 1, 4])

    # 登录卡片
    with login_col:
        st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
        st.subheader("🔐 用户登录")
        with st.form("login_form"):
            login_username = st.text_input("登录账号")
            login_password = st.text_input("密码", type="password")
            submit_login = st.form_submit_button("登录", use_container_width=True)

        if submit_login:
            success, result = login_user(login_username, login_password)
            if success:
                st.session_state.login_status = True
                st.session_state.user_info = result
                st.success("登录成功！正在跳转...")
                st.rerun()
            else:
                st.error(result)
        st.markdown("</div>", unsafe_allow_html=True)

    # 注册卡片
    with register_col:
        st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
        st.subheader("📝 账号注册")
        with st.form("register_form"):
            new_username = st.text_input("设置登录账号")
            new_realname = st.text_input("设置真实姓名（问诊时展示）")
            new_password = st.text_input("设置密码", type="password")
            confirm_password = st.text_input("确认密码", type="password")
            submit_register = st.form_submit_button("注册账号", use_container_width=True)

        if submit_register:
            if not new_username.strip() or not new_realname.strip() or not new_password.strip():
                st.error("登录账号、真实姓名、密码均不能为空")
            elif new_password != confirm_password:
                st.error("两次输入的密码不一致")
            else:
                from data import register_user

                success, msg = register_user(new_username, new_password, new_realname, role="user")
                if success:
                    st.success("注册成功！请切换到登录页登录")
                else:
                    st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: center; color: var(--text-weak); margin-top: 3rem;'>{COMPLIANCE_WARNING}</p>",
                unsafe_allow_html=True)
    st.stop()

# ========== 已登录：顶部信息 ==========
st.markdown(
    f"<p style='color: var(--text-secondary); margin-bottom: 0.3rem;'>当前用户：{st.session_state.user_info['real_name']} | 登录账号：{st.session_state.user_info['username']} | 角色：{st.session_state.user_info['role']}</p>",
    unsafe_allow_html=True)
st.markdown(f"<p style='color: var(--text-weak); font-size: 13px; margin-bottom: 1rem;'>{COMPLIANCE_WARNING}</p>",
            unsafe_allow_html=True)
st.divider()

# ========== 侧边栏菜单 ==========
with st.sidebar:
    st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem;'>🏥 功能导航</h3>", unsafe_allow_html=True)

    # 普通用户菜单
    menu_items = [
        "🤝 多模态联合问诊",
        "💬 文字问诊",
        "🖼️ 病灶图片识别",
        "📋 个人病历本",
        "👤 个人中心"
    ]
    menu_icons = [
        "handshake",
        "chat-left-text",
        "image",
        "journal-text",
        "person"
    ]

    # 管理员额外菜单
    if st.session_state.user_info['role'] == "admin":
        menu_items += [
            "📊 管理看板",
            "👥 用户管理",
            "📑 报告审核"
        ]
        menu_icons += [
            "bar-chart-line",
            "people",
            "file-earmark-text"
        ]

    # 渲染菜单
    selected_menu = option_menu(
        menu_title=None,
        options=menu_items,
        icons=menu_icons,
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "var(--text-secondary)", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "0.2rem 0.5rem",
                "padding": "0.75rem 1rem",
                "border-radius": "8px",
                "color": "var(--text-secondary)",
                "transition": "all 0.3s ease"
            },
            "nav-link-selected": {
                "background-color": "var(--primary-color)",
                "color": "white",
                "font-weight": "500"
            }
        }
    )

    # 退出登录
    st.divider()
    if st.button("退出登录", use_container_width=True, key="logout_btn"):
        st.session_state.login_status = False
        st.session_state.user_info = None
        st.rerun()

# ========== 页面渲染 ==========
# 核心功能页面
if selected_menu == "🤝 多模态联合问诊":
    render_multimodal_page()
elif selected_menu == "💬 文字问诊":
    render_text_consult_page()
elif selected_menu == "🖼️ 病灶图片识别":
    render_image_recognize_page()
elif selected_menu == "📋 个人病历本":
    render_medical_record_page()
elif selected_menu == "👤 个人中心":
    render_user_center_page()

# 管理员页面
elif st.session_state.user_info['role'] == "admin":
    if selected_menu == "📊 管理看板":
        render_admin_dashboard()
    elif selected_menu == "👥 用户管理":
        render_user_manage()
    elif selected_menu == "📑 报告审核":
        render_record_audit()