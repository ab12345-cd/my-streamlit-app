# 图片标注工具
import cv2
import numpy as np
from PIL import Image

def cv2_to_pil(cv2_img):
    """OpenCV图片转PIL，用于Streamlit显示"""
    return Image.fromarray(cv2_img)

def pil_to_cv2(pil_img):
    """PIL图片转OpenCV"""
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)