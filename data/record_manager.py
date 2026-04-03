# 病历记录管理（重构：按user_id匹配归属）
import os
from config.paths import RECORDS_DIR
from utils.file_utils import save_json, load_json, list_files
from utils.time_utils import parse_time_str

def save_record(record):
    """保存一条病历记录，强制绑定user_id"""
    # 姓名标准化，仅用于展示，不用于匹配
    if 'name' in record:
        record['name'] = record['name'].strip()
    # 确保lesions里没有不可序列化内容
    if 'lesions' in record:
        for lesion in record['lesions']:
            if 'mask' in lesion:
                lesion.pop('mask')
            if 'box' in lesion and hasattr(lesion['box'], 'tolist'):
                lesion['box'] = lesion['box'].tolist()
    # 获取用户ID，确保存在
    user_id = record.get('user_id', 'unknown')
    # 创建用户文件夹
    user_dir = os.path.join(RECORDS_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    # 保存文件到用户文件夹
    file_name = f"{record['time']}_{record['type']}.json"
    file_path = os.path.join(user_dir, file_name)
    save_json(file_path, record)
    return file_path

def load_all_records():
    """加载所有病历记录，损坏文件自动跳过"""
    record_list = []
    # 遍历所有用户文件夹
    if os.path.exists(RECORDS_DIR):
        for user_id in os.listdir(RECORDS_DIR):
            user_dir = os.path.join(RECORDS_DIR, user_id)
            # 确保是文件夹
            if os.path.isdir(user_dir):
                # 加载该用户的所有记录文件
                record_files = list_files(user_dir)
                for file_name in record_files:
                    file_path = os.path.join(user_dir, file_name)
                    try:
                        record = load_json(file_path)
                        # 兼容旧记录，补充必填字段
                        default_fields = {
                            "user_id": user_id,  # 核心：用户ID，用于归属匹配
                            "name": "未登记患者",
                            "age": "未登记",
                            "gender": "未登记",
                            "medical_history": "无特殊既往史",
                            "input": "",
                            "image_path": "",
                            "lesions": []
                        }
                        for key, default_value in default_fields.items():
                            if key not in record:
                                record[key] = default_value
                        record['file_name'] = file_name
                        record_list.append(record)
                    except Exception as e:
                        print(f"跳过损坏的记录文件：{os.path.join(user_id, file_name)}，错误：{e}")
                        continue
    return record_list

def filter_records(records, user_id=None, name=None, record_type=None, date_range=None):
    """
    多维度筛选病历记录，核心按user_id过滤归属
    :param records: 全量记录列表
    :param user_id: 用户唯一ID（核心过滤，普通用户必传）
    :param name: 患者姓名（仅用于管理员筛选）
    :param record_type: 诊断类型
    :param date_range: 时间范围元组
    :return: 筛选后的记录列表
    """
    filtered = records.copy()
    # 核心：按用户ID过滤归属，普通用户只能看到自己的记录
    if user_id and user_id != "all":
        filtered = [r for r in filtered if r['user_id'] == user_id]
    # 姓名筛选（仅管理员用）
    if name and name != "全部患者":
        name_std = name.strip()
        filtered = [r for r in filtered if r['name'] == name_std]
    # 类型筛选
    if record_type and record_type != "全部类型":
        filtered = [r for r in filtered if r['type'] == record_type]
    # 时间筛选
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = [
            r for r in filtered
            if start_date <= parse_time_str(r['time']) <= end_date
        ]
    return filtered

def get_all_patient_names(records):
    """获取所有患者姓名列表（管理员用）"""
    return sorted(list(set([r['name'].strip() for r in records])))

def get_all_record_types(records):
    """获取所有诊断类型列表"""
    return sorted(list(set([r['type'] for r in records])))

def get_user_record_count(user_id):
    """获取指定用户的问诊记录总数"""
    all_records = load_all_records()
    return len([r for r in all_records if r['user_id'] == user_id])