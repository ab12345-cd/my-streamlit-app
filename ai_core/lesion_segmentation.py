# 病灶识别标注模块（标准化版本）
import json
import os
import re
from http import HTTPStatus
from typing import List, Tuple, Dict, Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import dashscope
from dashscope import MultiModalConversation

from config.settings import DASHSCOPE_API_KEY, IMAGE_MODEL

# 环境变量配置
os.environ['PYTHONUTF8'] = '1'
os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY
dashscope.api_key = DASHSCOPE_API_KEY


class LesionAnnotationConfig:
    """病灶标注配置类"""
    # 识别配置
    MIN_CONFIDENCE = 80  # 最低置信度阈值
    CV_MIN_AREA = 200  # CV 识别最小面积

    # 标注样式配置
    FONT_PATH = "C:/Windows/Fonts/simsun.ttc"
    FONT_SIZE = 28
    BOX_COLOR = (255, 0, 0)  # RGB 红色
    BOX_WIDTH = 4
    TEXT_BG_COLOR = (255, 0, 0)
    TEXT_COLOR = (255, 255, 255)

    # 支持的病灶类型
    LESION_TYPES = [
        "口腔溃疡", "口腔破损", "皮疹", "红斑", "伤口",
        "淤青", "红肿", "脓包", "疣体", "痣", "异常色块"
    ]


def get_lesion_annotation(image_path: str) -> Tuple[Image.Image, List[Dict[str, Any]]]:
    """
    医疗专属病灶识别标注

    Args:
        image_path: 图片文件路径

    Returns:
        tuple: (标注后的 PIL 图片，病灶列表)
    """
    lesion_list: List[Dict[str, Any]] = []
    annotated_image: Image.Image = None

    # 1. 图片读取与验证
    img_data = _load_image(image_path)
    if img_data is None:
        return _create_default_result()

    try:
        img_np = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_height, img_width = img_rgb.shape[:2]
        annotated_image = Image.fromarray(img_rgb)
    except Exception as e:
        print(f"图片解码失败：{e}")
        return _create_default_result()

    # 2. AI 大模型识别
    ai_lesions = _ai_recognition(image_path, img_width, img_height)

    # 3. CV 兜底识别
    final_lesions = ai_lesions if ai_lesions else _cv_recognition(img)

    # 4. 绘制标注
    if final_lesions:
        lesion_list = _draw_annotations(
            annotated_image,
            final_lesions,
            img_width,
            img_height
        )

    return annotated_image, lesion_list


def _load_image(image_path: str) -> bytes:
    """加载图片数据"""
    if not os.path.exists(image_path):
        print(f"图片不存在：{image_path}")
        return None

    try:
        with open(image_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"图片读取失败：{e}")
        return None


def _create_default_result() -> Tuple[Image.Image, List[Dict[str, Any]]]:
    """创建默认空结果"""
    default_img = Image.new('RGB', (500, 500), color='white')
    return default_img, []


def _ai_recognition(image_path: str, img_width: int, img_height: int) -> List[Dict[str, Any]]:
    """AI 大模型识别"""
    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": f"file://{image_path}"},
                    {"text": _build_recognition_prompt(img_width, img_height)}
                ]
            }
        ]

        response = MultiModalConversation.call(
            model=IMAGE_MODEL,
            messages=messages,
            temperature=0.2,
            timeout=60
        )

        if response.status_code == HTTPStatus.OK:
            response_text = response.output.choices[0].message.content[0]["text"].strip()
            return _parse_ai_response(response_text)
    except Exception as e:
        print(f"大模型识别失败：{e}")

    return []


def _build_recognition_prompt(img_width: int, img_height: int) -> str:
    """构建识别提示词"""
    return f"""
你是一名专业的口腔皮肤科医生，请精准识别图片中的所有病灶。

【图片信息】
宽度：{img_width}像素，高度：{img_height}像素

【识别目标】
必须识别以下类型的病灶：{', '.join(LesionAnnotationConfig.LESION_TYPES)}

【输出规范】
1. 只输出纯 JSON 格式，不要有任何其他文字或解释
2. JSON 格式严格遵循：
{{
  "lesions": [
    {{
      "name": "病灶名称（必须是中文）",
      "bbox": [x1, y1, x2, y2],
      "confidence": 95
    }}
  ]
}}

【技术要求】
- bbox: 整数坐标 [x1, y1, x2, y2]，严格贴合病灶边缘
- confidence: 0-100 的整数，必须≥{LesionAnnotationConfig.MIN_CONFIDENCE}
- 即使是很小的病灶，只要与周围组织颜色/形态不同就必须识别
- 无病灶时输出：{{"lesions": []}}

【示例】
{{"lesions": [{{"name": "口腔溃疡", "bbox": [180, 420, 350, 580], "confidence": 95}}]}}
"""


def _parse_ai_response(response_text: str) -> List[Dict[str, Any]]:
    """解析 AI 响应"""
    try:
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_text = json_match.group()
            result = json.loads(json_text)
            lesions = result.get('lesions', [])

            # 数据验证
            validated = []
            for lesion in lesions:
                if _validate_lesion(lesion):
                    validated.append(lesion)
            return validated
    except Exception as e:
        print(f"AI 响应解析失败：{e}")

    return []


def _validate_lesion(lesion: Dict[str, Any]) -> bool:
    """验证病灶数据有效性"""
    try:
        # 检查必填字段
        if not all(k in lesion for k in ['name', 'bbox', 'confidence']):
            return False

        # 验证置信度
        confidence = int(lesion['confidence'])
        if confidence < LesionAnnotationConfig.MIN_CONFIDENCE:
            return False

        # 验证坐标格式
        bbox = lesion['bbox']
        if not isinstance(bbox, list) or len(bbox) != 4:
            return False

        # 验证坐标值
        coords = [int(x) for x in bbox]
        if any(c < 0 for c in coords):
            return False

        return True
    except Exception:
        return False


def _cv_recognition(img: np.ndarray) -> List[Dict[str, Any]]:
    """传统 CV 兜底识别"""
    try:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 红色区域检测（炎症、红斑）
        lower_red = np.array([0, 30, 30])
        upper_red = np.array([20, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red, upper_red)

        # 白色区域检测（溃疡、脓包）
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)

        # 合并掩膜
        mask = cv2.bitwise_or(mask_red, mask_white)

        # 形态学操作去噪
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # 轮廓检测
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        lesions = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > LesionAnnotationConfig.CV_MIN_AREA:
                x, y, w, h = cv2.boundingRect(cnt)
                lesions.append({
                    "name": "异常病灶区域",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 85
                })

        return lesions
    except Exception as e:
        print(f"CV 兜底识别失败：{e}")
        return []


def _draw_annotations(
        image: Image.Image,
        lesions: List[Dict[str, Any]],
        img_width: int,
        img_height: int
) -> List[Dict[str, Any]]:
    """绘制标注并返回结构化数据"""
    draw = ImageDraw.Draw(image)

    # 加载字体
    font = _load_font()

    lesion_list = []
    for lesion in lesions:
        bbox = lesion.get('bbox', [0, 0, 0, 0])
        if not _validate_bbox(bbox):
            continue

        # 坐标转换与边界检查
        x1, y1, x2, y2 = _normalize_bbox(bbox, img_width, img_height)
        if x2 <= x1 or y2 <= y1:
            continue

        # 绘制矩形框
        draw.rectangle(
            [x1, y1, x2, y2],
            outline=LesionAnnotationConfig.BOX_COLOR,
            width=LesionAnnotationConfig.BOX_WIDTH
        )

        # 绘制文字标签
        name = lesion.get('name', '异常病灶')
        conf = int(lesion.get('confidence', 85))
        text = f"{name} {conf}%"

        # 计算文字位置，确保在图像内
        text_y = y1 - 40
        if text_y < 30:  # 确保文字不会超出图像顶部
            text_y = y2 + 10
            if text_y + 30 > img_height:  # 确保文字不会超出图像底部
                text_y = y1 - 20
                if text_y < 10:
                    text_y = 10

        # 计算文字背景框
        text_bbox = draw.textbbox((x1, text_y), text, font=font)
        
        # 确保文字背景框在图像内
        text_x = x1
        if text_bbox[2] > img_width:
            text_x = img_width - (text_bbox[2] - text_bbox[0]) - 10
            if text_x < 0:
                text_x = 0

        # 重新计算文字边界框
        text_bbox = draw.textbbox((text_x, text_y), text, font=font)
        
        # 绘制文字背景框
        draw.rectangle(
            [
                text_bbox[0] - 5,
                text_bbox[1] - 5,
                text_bbox[2] + 5,
                text_bbox[3] + 5
            ],
            fill=LesionAnnotationConfig.TEXT_BG_COLOR
        )
        
        # 绘制文字
        draw.text(
            (text_x, text_y),
            text,
            font=font,
            fill=LesionAnnotationConfig.TEXT_COLOR
        )

        # 记录结构化数据
        area = (x2 - x1) * (y2 - y1)
        lesion_list.append({
            "病灶名称": name,
            "置信度 (%)": conf,
            "病灶面积 (像素)": area,
            "坐标": [x1, y1, x2, y2]
        })

    return lesion_list


def _load_font() -> ImageFont.FreeTypeFont:
    """加载中文字体"""
    try:
        # 尝试加载指定字体
        return ImageFont.truetype(
            LesionAnnotationConfig.FONT_PATH,
            LesionAnnotationConfig.FONT_SIZE
        )
    except Exception:
        try:
            # 尝试加载其他常见中文字体
            common_fonts = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/arial.ttf"  # 备用英文字体
            ]
            for font_path in common_fonts:
                try:
                    return ImageFont.truetype(font_path, LesionAnnotationConfig.FONT_SIZE)
                except Exception:
                    continue
        except Exception:
            pass
        # 使用默认字体
        return ImageFont.load_default()


def _validate_bbox(bbox: List[int]) -> bool:
    """验证边界框有效性"""
    if not isinstance(bbox, list) or len(bbox) != 4:
        return False
    try:
        coords = [int(x) for x in bbox]
        return all(c >= 0 for c in coords)
    except Exception:
        return False


def _normalize_bbox(
        bbox: List[int],
        img_width: int,
        img_height: int
) -> Tuple[int, int, int, int]:
    """标准化边界框坐标"""
    x1, y1, x2, y2 = [int(x) for x in bbox]

    x1 = max(0, min(x1, img_width))
    y1 = max(0, min(y1, img_height))
    x2 = max(0, min(x2, img_width))
    y2 = max(0, min(y2, img_height))

    return x1, y1, x2, y2
