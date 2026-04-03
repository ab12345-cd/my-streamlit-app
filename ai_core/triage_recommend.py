# 智能分诊推荐核心逻辑（修复导入）
import os
os.environ['PYTHONUTF8'] = '1'
from config.settings import DASHSCOPE_API_KEY, TEXT_MODEL

os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY
import dashscope
from dashscope import Generation
from http import HTTPStatus
from config.settings import DASHSCOPE_API_KEY, TRIAGE_MODEL
import json

# 设置API Key
dashscope.api_key = DASHSCOPE_API_KEY


def get_triage_result(patient_info, symptom_desc, diagnosis_result):
    """
    根据患者信息和诊断结果，生成分诊推荐
    """
    prompt = f"""
    你是医院的分诊台护士，根据患者的情况，给出专业的分诊推荐，严格按JSON格式输出，不要加其他内容。
    【患者信息】
    姓名：{patient_info['name']}
    年龄：{patient_info['age']}岁
    性别：{patient_info['gender']}
    症状描述：{symptom_desc}
    诊断结果：{diagnosis_result}

    【输出要求】
    严格按JSON格式输出，包含以下字段：
    1. "department": 推荐就诊科室，如：口腔科、皮肤科、呼吸内科、急诊科
    2. "risk_level": 风险等级，只能是：低风险、中风险、高风险
    3. "risk_desc": 风险说明，100字以内
    4. "warning": 就诊提醒，100字以内

    【输出示例】
    {{"department": "口腔科", "risk_level": "低风险", "risk_desc": "患者为口腔溃疡，无全身症状，风险较低", "warning": "建议1周内症状无缓解前往口腔科就诊"}}

    只输出纯JSON，不要加其他任何内容！
    """

    response = Generation.call(
        model=TRIAGE_MODEL,
        prompt=prompt,
        temperature=0.1,
        max_tokens=500
    )

    if response.status_code == HTTPStatus.OK:
        try:
            import re
            import json
            response_text = response.output.text.strip()
            json_text = re.search(r'\{[\s\S]*\}', response_text).group()
            return json.loads(json_text)
        except:
            return {
                "department": "全科医学科",
                "risk_level": "低风险",
                "risk_desc": "患者情况较为平稳，建议全科初步评估",
                "warning": "如症状加重请及时前往医院就诊"
            }
    else:
        raise Exception(f"分诊生成失败：{response.message}")