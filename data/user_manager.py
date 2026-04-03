# 用户管理模块（重构：用户名与真实姓名分离+唯一ID）
import os
import uuid
from config.paths import USER_DATA_DIR
from utils.file_utils import save_json, load_json, list_files
from utils.time_utils import get_safe_time_str

# 初始化管理员账号
def init_admin_user():
    """初始化默认管理员账号"""
    admin_path = os.path.join(USER_DATA_DIR, "admin.json")
    if not os.path.exists(admin_path):
        admin_user = {
            "user_id": str(uuid.uuid4()),  # 唯一用户ID
            "username": "admin",  # 登录账号
            "real_name": "系统管理员",  # 真实姓名
            "password": "admin123",
            "role": "admin",  # 角色：admin/user
            "create_time": "2026-01-01 00:00:00"
        }
        save_json(admin_path, admin_user)


def register_user(username, password, real_name, role="user"):
    """
    注册新用户
    :param username: 登录账号（唯一）
    :param password: 密码
    :param real_name: 真实姓名
    :param role: 角色，默认普通用户
    :return: (是否成功, 提示信息)
    """
    # 检查用户名是否已存在
    user_files = list_files(USER_DATA_DIR)
    for file_name in user_files:
        user = load_json(os.path.join(USER_DATA_DIR, file_name))
        if user['username'] == username.strip():
            return False, "用户名已存在"

    # 创建新用户
    new_user = {
        "user_id": str(uuid.uuid4()),
        "username": username.strip(),
        "real_name": real_name.strip(),
        "password": password,
        "role": role,
        "create_time": get_safe_time_str()
    }
    save_json(os.path.join(USER_DATA_DIR, f"{username}.json"), new_user)
    return True, "注册成功"


def login_user(username, password):
    """
    用户登录
    :param username: 登录账号
    :param password: 密码
    :return: (是否成功, 用户信息/错误信息)
    """
    user_path = os.path.join(USER_DATA_DIR, f"{username.strip()}.json")
    if not os.path.exists(user_path):
        return False, "用户不存在"
    user = load_json(user_path)
    if user['password'] != password:
        return False, "密码错误"
    # 登录成功，返回用户核心信息
    return True, {
        "user_id": user['user_id'],
        "username": user['username'],
        "real_name": user['real_name'],
        "role": user['role']
    }


def get_all_users():
    """获取所有用户列表（管理员用）"""
    user_list = []
    user_files = list_files(USER_DATA_DIR)
    for file_name in user_files:
        user = load_json(os.path.join(USER_DATA_DIR, file_name))
        user_list.append({
            "user_id": user['user_id'],
            "username": user['username'],
            "real_name": user['real_name'],
            "role": user['role'],
            "create_time": user['create_time']
        })
    return user_list


def update_user_info(user_id, new_real_name=None, new_password=None):
    """修改用户信息（真实姓名/密码）"""
    user_files = list_files(USER_DATA_DIR)
    for file_name in user_files:
        user_path = os.path.join(USER_DATA_DIR, file_name)
        user = load_json(user_path)
        if user['user_id'] == user_id:
            if new_real_name:
                user['real_name'] = new_real_name.strip()
            if new_password:
                user['password'] = new_password
            save_json(user_path, user)
            return True, "修改成功"
    return False, "用户不存在"


# 初始化管理员账号
init_admin_user()