# 文件工具类（彻底修复中文编码问题）
import os
import json

def save_json(file_path, data):
    """保存JSON文件，强制utf-8编码，支持中文"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(file_path):
    """加载JSON文件，强制utf-8编码，支持中文"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_files(dir_path, suffix=".json"):
    """列出目录下指定后缀的文件"""
    if not os.path.exists(dir_path):
        return []
    return [f for f in os.listdir(dir_path) if f.endswith(suffix)]