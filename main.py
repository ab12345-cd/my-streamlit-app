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

# 后面是你原来的main.py代码...
# ... existing code ...

import streamlit as st
from config.settings import PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT, COMPLIANCE_WARNING
from data import login_user, register_user, init_admin_user
from ui_pages import (
    render_text_consult_page,
    render_image_recognize_page,
    render_multimodal_page,
    render_medical_record_page,
    render_user_center_page
)
from ui_pages.admin import render_admin_dashboard, render_user_manage, render_record_audit
from utils.time_utils import get_safe_time_str

# ... existing code ...


# 页面全局配置
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT
)

# 全局样式
st.markdown("""
<style>
    /* 全局布局 */
    .main {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 标题样式 */
    h1 {
        color: #1a73e8;
        text-align: center;
        font-weight: 700;
        margin-bottom: 1.5rem;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #333;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #555;
        font-weight: 500;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }
    
    /* 按钮样式 */
    .stButton>button {
        background-color: #1a73e8;
        color: white;
        border-radius: 10px;
        height: 48px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 4px rgba(26, 115, 232, 0.3);
    }
    
    .stButton>button:hover {
        background-color: #1765cc;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(26, 115, 232, 0.4);
    }
    
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(26, 115, 232, 0.3);
    }
    
    /* 次要按钮 */
    .stButton>button[kind="secondary"] {
        background-color: #f1f3f4;
        color: #333;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton>button[kind="secondary"]:hover {
        background-color: #e8eaed;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 56px;
        border-radius: 12px 12px 0 0;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f1f3f4;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #e8f0fe;
        color: #1a73e8;
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #e8eaed;
        padding: 12px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #1a73e8;
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
    }
    
    /* 卡片样式 */
    .stCard {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: white;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e8eaed;
        padding: 1.5rem;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #1a73e8;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    
    /* 单选按钮样式 */
    .stRadio>div {
        gap: 12px;
    }
    
    .stRadio label {
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stRadio label:hover {
        color: #1a73e8;
    }
    
    /* 分隔线样式 */
    hr {
        border: 1px solid #e8eaed;
        margin: 1.5rem 0;
    }
    
    /* 信息提示样式 */
    .stInfo {
        border-radius: 8px;
        padding: 1rem;
        background-color: #e8f0fe;
        border-left: 4px solid #1a73e8;
    }
    
    /* 成功提示样式 */
    .stSuccess {
        border-radius: 8px;
        padding: 1rem;
        background-color: #e6f4ea;
        border-left: 4px solid #34a853;
    }
    
    /* 错误提示样式 */
    .stError {
        border-radius: 8px;
        padding: 1rem;
        background-color: #fce8e6;
        border-left: 4px solid #ea4335;
    }
    
    /* 加载动画 */
    .stSpinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        
        .stButton>button {
            height: 44px;
            font-size: 0.9rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 48px;
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 初始化管理员账号
init_admin_user()

# 会话状态初始化
if "login_status" not in st.session_state:
    st.session_state.login_status = False
    st.session_state.user_info = None

# 未登录：显示登录+注册页面
if not st.session_state.login_status:
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    # 登录/注册选项卡
    login_tab, register_tab = st.tabs(["用户登录", "账号注册"])

    # 登录选项卡
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("登录账号")
            password = st.text_input("密码", type="password")
            submit_login = st.form_submit_button("登录", width="stretch")

        if submit_login:
            success, result = login_user(username, password)
            if success:
                st.session_state.login_status = True
                st.session_state.user_info = result
                st.success("登录成功！正在跳转...")
                st.rerun()
            else:
                st.error(result)

    # 注册选项卡（新增真实姓名输入）
    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("设置登录账号")
            new_realname = st.text_input("设置真实姓名（问诊时展示）")
            new_password = st.text_input("设置密码", type="password")
            confirm_password = st.text_input("确认密码", type="password")
            submit_register = st.form_submit_button("注册账号", width="stretch")

        if submit_register:
            if not new_username.strip() or not new_realname.strip() or not new_password.strip():
                st.error("登录账号、真实姓名、密码均不能为空")
            elif new_password != confirm_password:
                st.error("两次输入的密码不一致")
            else:
                success, msg = register_user(new_username, new_password, new_realname, role="user")
                if success:
                    st.success("注册成功！请切换到登录页登录")
                else:
                    st.error(msg)

    # 默认管理员账号提示
    st.info("默认管理员账号：admin / 密码：admin123")
    st.stop()

# 已登录：显示系统
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
if st.session_state.user_info:
    st.caption(
        f"当前用户：{st.session_state.user_info['real_name']} | 登录账号：{st.session_state.user_info['username']} | 角色：{st.session_state.user_info['role']}")
else:
    st.caption("当前用户：未登录")
st.caption(COMPLIANCE_WARNING)

# ========== 侧边栏导航 ==========
with st.sidebar:
    st.markdown("### 📋 功能导航")
    # 所有用户通用功能
    menu_options = [
        "💬 智能文字问诊",
        "🖼️ 病灶图片识别",
        "🤝 多模态联合诊断",
        "📋 个人病历本",
        "👤 个人中心"
    ]
    # 管理员额外功能
    if st.session_state.user_info and st.session_state.user_info.get('role') == "admin":
        menu_options += [
            "📊 管理看板",
            "👥 用户管理",
            "📑 报告审核"
        ]

    # 导航选择
    selected_menu = st.radio("选择功能", menu_options, label_visibility="collapsed")

    # 退出登录按钮
    st.divider()
    if st.button("退出登录", width="stretch", type="secondary"):
        st.session_state.login_status = False
        st.session_state.user_info = None
        st.rerun()

# ========== 页面渲染 ==========
# 通用功能
if selected_menu == "💬 智能文字问诊":
    render_text_consult_page()
elif selected_menu == "🖼️ 病灶图片识别":
    render_image_recognize_page()
elif selected_menu == "🤝 多模态联合诊断":
    render_multimodal_page()
elif selected_menu == "📋 个人病历本":
    render_medical_record_page()
elif selected_menu == "👤 个人中心":
    render_user_center_page()

# 管理员功能
elif st.session_state.user_info['role'] == "admin":
    if selected_menu == "📊 管理看板":
        render_admin_dashboard()
    elif selected_menu == "👥 用户管理":
        render_user_manage()
    elif selected_menu == "📑 报告审核":
        render_record_audit()