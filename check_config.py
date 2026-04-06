# 一键检查配置文件脚本
import os
import sys


def check_config():
    print("=" * 60)
    print("🔍 开始检查配置文件...")
    print("=" * 60)

    # 1. 检查config/settings.py是否存在
    settings_path = os.path.join(os.path.dirname(__file__), "config", "settings.py")
    if not os.path.exists(settings_path):
        print("❌ 错误：config/settings.py 文件不存在")
        return False
    print("✅ config/settings.py 文件存在")

    # 2. 尝试导入配置文件
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from config.settings import (
            PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT,
            COMPLIANCE_WARNING, COMPLIANCE_FOOTER,
            DASHSCOPE_API_KEY,
            TEXT_MODEL, IMAGE_MODEL, MULTIMODAL_MODEL, TRIAGE_MODEL
        )
        print("✅ 所有配置变量导入成功")
        print(f"   - 页面标题：{PAGE_TITLE}")
        print(f"   - 文本模型：{TEXT_MODEL}")
        print(f"   - 多模态模型：{MULTIMODAL_MODEL}")
        print(f"   - 分诊模型：{TRIAGE_MODEL}")
    except ImportError as e:
        print(f"❌ 配置导入失败：{e}")
        return False

    # 3. 检查config/paths.py是否存在
    paths_path = os.path.join(os.path.dirname(__file__), "config", "paths.py")
    if not os.path.exists(paths_path):
        print("❌ 错误：config/paths.py 文件不存在")
        return False
    print("✅ config/paths.py 文件存在")

    # 4. 检查存储目录
    try:
        from config.paths import (
            BASE_DIR, STORAGE_DIR, UPLOADS_DIR,
            RECORDS_DIR, USER_DATA_DIR
        )
        print("✅ 所有路径配置导入成功")
        print(f"   - 项目根目录：{BASE_DIR}")
        print(f"   - 存储目录：{STORAGE_DIR}")
        print(f"   - 上传目录：{UPLOADS_DIR}")
        print(f"   - 病历目录：{RECORDS_DIR}")
        print(f"   - 用户目录：{USER_DATA_DIR}")
    except ImportError as e:
        print(f"❌ 路径导入失败：{e}")
        return False

    print("=" * 60)
    print("✅ 所有配置检查通过！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    check_config()
    input("\n按回车键退出...")