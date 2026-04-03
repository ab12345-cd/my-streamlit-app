# 项目全局配置文件（终极全量版，彻底解决所有导入错误）
import os

# ========== 页面配置 ==========
PAGE_TITLE = "AI多模态医疗辅助问诊系统"
PAGE_ICON = "🏥"
PAGE_LAYOUT = "wide"

# ========== 全局合规声明 ==========
# 全局合规声明（简化版，无大格式）
COMPLIANCE_WARNING = "⚠ 本系统仅用于健康科普辅助，不替代专业医生诊断与治疗，身体不适请及时前往正规医院就诊"
# 【修改】简化AI结果末尾的声明，去掉大格式
COMPLIANCE_FOOTER = "⚠ 合规声明：本内容仅为健康科普辅助参考，不具备法律效力，不能替代执业医师的面诊与诊断。身体不适请及时前往正规医院就诊，请勿根据本内容自行用药。"
# ========== 通义千问API Key（请替换为你的真实API Key） ==========
DASHSCOPE_API_KEY = "sk-a46d2830d59f459d8c2a3c6ec5a81bf2"

# ========== 模型配置（全量覆盖所有模块，彻底解决导入错误） ==========
# 文本问诊/分诊/通用文本模型
TEXT_MODEL = "qwen-turbo"
TRIAGE_MODEL = "qwen-turbo"
SPEECH_MODEL = "qwen-turbo"  # 语音识别模型
# 多模态/图片识别/病灶标注模型
IMAGE_MODEL = "qwen-vl-max"
MULTIMODAL_MODEL = "qwen-vl-max"
VISION_MODEL = "qwen-vl-max"
# 病灶分割备用模型
SEGMENTATION_MODEL = "yolov8n-seg.pt"

# ========== 路径配置 ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

# ========== 百度语音 API 配置 ==========
# 请在百度智能云官网申请：

