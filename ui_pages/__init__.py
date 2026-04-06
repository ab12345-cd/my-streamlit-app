# ui_pages/__init__.py（彻底修复导入错误）
from .text_consult_page import render_text_consult_page
from .image_recognize_page import render_image_recognize_page
from .multimodal_page import render_multimodal_page
from .medical_record_page import render_medical_record_page
from .user_center_page import render_user_center_page

__all__ = [
    "render_text_consult_page",
    "render_image_recognize_page",
    "render_multimodal_page",
    "render_medical_record_page",
    "render_user_center_page"
]