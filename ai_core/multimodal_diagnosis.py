# 多模态联合诊断核心逻辑（修复导入）
import os
os.environ['PYTHONUTF8'] = '1'
from config.settings import DASHSCOPE_API_KEY, TEXT_MODEL

os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY
import dashscope
from dashscope import MultiModalConversation
from http import HTTPStatus
from config.settings import DASHSCOPE_API_KEY, MULTIMODAL_MODEL, COMPLIANCE_FOOTER

# 设置API Key
dashscope.api_key = DASHSCOPE_API_KEY


def get_multimodal_diagnosis_result(patient_info, symptom_desc, image_path):
    """
    多模态联合诊断：结合文字症状和图片，给出综合诊断分析
    """
    prompt = f"""
    你是一名经验丰富的全科医生，结合患者的文字症状描述和病灶图片，给出综合的辅助诊断分析。
    【患者信息】
    姓名：{patient_info['name']}
    年龄：{patient_info['age']}岁
    性别：{patient_info['gender']}
    既往病史/过敏史：{patient_info['medical_history'] if patient_info['medical_history'] else '无'}

    【症状描述】
    {symptom_desc}

    【输出要求】
    1. 结合图片和文字，综合分析，分点输出：病灶特征描述、初步判断、可能原因、建议措施、就诊建议
    2. 结构清晰，语言通俗易懂，严谨专业
    3. 禁止推荐处方药，禁止给出明确的治疗方案，仅做健康科普辅助
    """

    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"file://{image_path}"},
                {"text": prompt}
            ]
        }
    ]

    response = MultiModalConversation.call(
        model=MULTIMODAL_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=2000
    )

    if response.status_code == HTTPStatus.OK:
        return response.output.choices[0].message.content[0]["text"].strip()
    else:
        raise Exception(f"多模态诊断失败：{response.message}")