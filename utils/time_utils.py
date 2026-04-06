# 时间工具函数
import datetime

def get_safe_time_str():
    """生成Windows兼容的安全时间字符串（无冒号）"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

def parse_time_str(time_str):
    """把时间字符串解析为datetime对象"""
    return datetime.datetime.strptime(time_str.split(" ")[0], "%Y-%m-%d").date()