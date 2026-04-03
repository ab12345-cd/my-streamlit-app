# 文字问诊核心逻辑（修复导入）
import os
os.environ['PYTHONUTF8'] = '1'
from config.settings import DASHSCOPE_API_KEY, TEXT_MODEL

os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY
import dashscope
from dashscope import Generation
from http import HTTPStatus
from config.settings import DASHSCOPE_API_KEY, TEXT_MODEL, COMPLIANCE_FOOTER

# 设置API Key
dashscope.api_key = DASHSCOPE_API_KEY


def get_text_diagnosis_result(patient_info, symptom_desc):
    """
    根据患者信息和症状描述，生成AI辅助诊断结果
    """
    prompt = f"""
    你是一名经验丰富的全科医生，根据患者的信息和症状描述，给出专业的辅助诊断分析。
    【患者信息】
    姓名：{patient_info['name']}
    年龄：{patient_info['age']}岁
    性别：{patient_info['gender']}
    既往病史/过敏史：{patient_info['medical_history'] if patient_info['medical_history'] else '无'}

    【症状描述】
    {symptom_desc}

    【输出要求】
    1. 分点输出，结构清晰，包含：初步判断、可能原因、建议措施、就诊建议
    2. 语言通俗易懂，严谨专业，不要使用过于生僻的医学术语
    3. 禁止推荐处方药，禁止给出明确的治疗方案，仅做健康科普辅助
    """

    response = Generation.call(
        model=TEXT_MODEL,
        prompt=prompt,
        temperature=0.3,
        max_tokens=2000
    )

    if response.status_code == HTTPStatus.OK:
        return response.output.text.strip()
    else:
        raise Exception(f"诊断生成失败：{response.message}")