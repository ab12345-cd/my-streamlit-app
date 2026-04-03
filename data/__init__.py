from .record_manager import (
    save_record,
    load_all_records,
    filter_records,
    get_all_patient_names,
    get_all_record_types,
    get_user_record_count
)
from .user_manager import (
    register_user,
    login_user,
    get_all_users,
    init_admin_user,
    update_user_info
)
__all__ = [
    # 记录管理
    "save_record",
    "load_all_records",
    "filter_records",
    "get_all_patient_names",
    "get_all_record_types",
    "get_user_record_count",
    # 用户管理
    "register_user",
    "login_user",
    "get_all_users",
    "update_user_info",
    "init_admin_user"
]