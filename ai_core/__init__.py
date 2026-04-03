# ai_core/__init__.py（全量修复版）
from .text_diagnosis import get_text_diagnosis_result
from .image_recognition import get_image_recognition_result
from .multimodal_diagnosis import get_multimodal_diagnosis_result
from .speech_recognition import speech_to_text
from .triage_recommend import get_triage_result
from .lesion_segmentation import get_lesion_annotation

__all__ = [
    "get_text_diagnosis_result",
    "get_image_recognition_result",
    "get_multimodal_diagnosis_result",
    "speech_to_text",
    "get_triage_result",
    "get_lesion_annotation"
]