# 图片识别诊断核心逻辑（修复导入）
# 强制设置dashscope API的编码
import os
os.environ['PYTHONUTF8'] = '1'
from config.settings import DASHSCOPE_API_KEY, TEXT_MODEL

os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY
import dashscope
from dashscope import MultiModalConversation
from http import HTTPStatus
from config.settings import DASHSCOPE_API_KEY, IMAGE_MODEL, COMPLIANCE_FOOTER

# 设置API Key
dashscope.api_key = DASHSCOPE_API_KEY


def get_image_recognition_result(patient_info, image_path, symptom_desc=""):
    """
    根据病灶图片，生成AI辅助诊断结果
    """
    prompt = f"""
    你是一名专业的皮肤科/口腔科医生，根据患者的病灶图片和信息，给出专业的辅助诊断分析。
    【患者信息】
    姓名：{patient_info['name']}
    年龄：{patient_info['age']}岁
    性别：{patient_info['gender']}
    既往病史/过敏史：{patient_info['medical_history'] if patient_info['medical_history'] else '无'}
    补充症状描述：{symptom_desc if symptom_desc else '无'}

    【输出要求】
    1. 先描述图片中看到的病灶特征，再给出初步判断、可能原因、建议措施、就诊建议
    2. 分点输出，结构清晰，语言通俗易懂，严谨专业
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
        model=IMAGE_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=2000
    )

    if response.status_code == HTTPStatus.OK:
        return response.output.choices[0].message.content[0]["text"].strip()
    else:
        raise Exception(f"图片诊断失败：{response.message}")