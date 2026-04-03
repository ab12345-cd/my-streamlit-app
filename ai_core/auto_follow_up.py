# 智能自动追问核心逻辑（优化：模拟真实医生问诊）
# 智能自动追问核心逻辑（优化：模拟真实医生问诊）
# 强制设置 dashscope API 的编码
import os
os.environ['PYTHONUTF8'] = '1'
from config.settings import DASHSCOPE_API_KEY, TEXT_MODEL

os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY

import json
import dashscope
from http import HTTPStatus

# ... existing code ...

from config.settings import TEXT_MODEL


def need_follow_up(dialog_history):
    """
    模拟真实医生问诊，判断是否需要追问关键信息
    :param dialog_history: 对话历史列表
    :return: 追问问题（字符串），不需要追问返回None
    """
    prompt = f"""
    你是一名经验丰富的门诊医生，正在和患者问诊。
    【规则】
    1. 你只能根据患者的对话，判断是否缺少关键问诊信息，只输出1个最关键的追问问题。
    2. 关键信息包括：发病时间、疼痛性质/程度、伴随症状、既往病史、诱因、是否做过检查/用药。
    3. 如果患者已经把关键信息说清楚了，直接输出【无需追问】，绝对不能提前给诊断、建议。
    4. 追问要口语化、简洁，像真实医生说话，不要太书面。
    5. 一次只问一个问题，不要一次问多个。

    【对话历史】
    {json.dumps(dialog_history, ensure_ascii=False)}

    输出：
    """

    response = dashscope.Generation.call(
        model=TEXT_MODEL,
        prompt=prompt,
        temperature=0.3,
        max_tokens=150
    )

    if response.status_code == HTTPStatus.OK:
        result = response.output.text.strip()
        if "无需追问" in result:
            return None
        else:
            return result
    else:
        raise Exception(f"追问判断失败：{response.message}")