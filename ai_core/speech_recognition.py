# 语音识别模块（修复导入错误）
import os
os.environ['PYTHONUTF8'] = '1'
from config.settings import DASHSCOPE_API_KEY, TEXT_MODEL

os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY
import dashscope
from dashscope import Generation
from http import HTTPStatus
from config.settings import DASHSCOPE_API_KEY, SPEECH_MODEL

# 设置API Key
dashscope.api_key = DASHSCOPE_API_KEY


def speech_to_text(audio_path):
    """
    语音转文字
    :param audio_path: 音频文件路径
    :return: 识别后的文本
    """
    prompt = f"请把这个音频里的内容转换成文字，只输出文字，不要加其他内容。音频文件路径：file://{audio_path}"

    response = Generation.call(
        model=SPEECH_MODEL,
        prompt=prompt,
        temperature=0.1,
        max_tokens=500
    )

    if response.status_code == HTTPStatus.OK:
        return response.output.text.strip()
    else:
        raise Exception(f"语音识别失败：{response.message}")