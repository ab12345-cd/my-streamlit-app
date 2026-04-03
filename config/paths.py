# 路径配置文件（修复：新增USER_DATA_DIR）
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 存储目录
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

# 上传文件目录
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# 病历记录目录
RECORDS_DIR = os.path.join(STORAGE_DIR, "records")
os.makedirs(RECORDS_DIR, exist_ok=True)

# 【新增】用户数据目录
USER_DATA_DIR = os.path.join(STORAGE_DIR, "users")
os.makedirs(USER_DATA_DIR, exist_ok=True)

# 模型缓存目录
MODEL_CACHE_DIR = os.path.join(STORAGE_DIR, "models")
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)