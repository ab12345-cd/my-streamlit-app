# 标准化医学PDF报告生成工具（修复表格溢出）
import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors


def generate_standard_medical_pdf(record, triage_result=None):
    """
    生成标准化医学报告，修复表格文字溢出问题
    :param record: 病历记录字典
    :param triage_result: 分诊结果字典（可选）
    :return: PDF文件流
    """
    buffer = io.BytesIO()

    # 字体注册
    try:
        pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
        pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
        font_body = 'SimSun'
        font_title = 'SimHei'
    except:
        font_body = 'Helvetica'
        font_title = 'Helvetica-Bold'

    # 样式定义（新增表格内文本样式，支持自动换行）
    style_report_title = ParagraphStyle(
        name='report_title', fontName=font_title, fontSize=22, alignment=TA_CENTER, leading=30, spaceAfter=20
    )
    style_table_text = ParagraphStyle(
        name='table_text', fontName=font_body, fontSize=10, alignment=TA_LEFT, leading=14, wordWrap='CJK'
    )
    style_table_center = ParagraphStyle(
        name='table_center', fontName=font_body, fontSize=10, alignment=TA_CENTER, leading=14
    )
    style_patient_info = ParagraphStyle(
        name='patient_info', fontName=font_body, fontSize=12, alignment=TA_LEFT, leading=20
    )
    style_chapter = ParagraphStyle(
        name='chapter', fontName=font_title, fontSize=14, alignment=TA_LEFT, leading=22, spaceBefore=15, spaceAfter=8
    )
    style_body = ParagraphStyle(
        name='body', fontName=font_body, fontSize=12, alignment=TA_LEFT, leading=18, leftIndent=10, spaceAfter=6,
        wordWrap='CJK'
    )
    style_list = ParagraphStyle(
        name='list', fontName=font_body, fontSize=12, alignment=TA_LEFT, leading=18, leftIndent=30, firstLineIndent=-20,
        spaceAfter=4
    )
    style_footer = ParagraphStyle(
        name='footer', fontName=font_body, fontSize=10, alignment=TA_CENTER, leading=12, textColor=colors.darkred
    )
    style_triage = ParagraphStyle(
        name='triage', fontName=font_title, fontSize=12, alignment=TA_CENTER, leading=18
    )

    # 文本预处理
    def clean_text(text):
        text = re.sub(r'#{1,3}\s*', '', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'^\s*[-*+]\s*', '● ', text, flags=re.M)
        text = text.replace('\r', '').strip()
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    # 构建报告内容
    story = []

    # 1. 报告标题
    story.append(Paragraph("AI医疗辅助问诊报告", style_report_title))
    story.append(Spacer(1, 10))

    # 2. 患者信息表格（修复溢出：用Paragraph填充，调整列宽）
    patient_data = [
        [
            Paragraph("姓名", style_table_center),
            Paragraph(record.get('name', '未登记'), style_table_center),
            Paragraph("性别", style_table_center),
            Paragraph(record.get('gender', '未登记'), style_table_center),
            Paragraph("年龄", style_table_center),
            Paragraph(f"{record.get('age', '未登记')}岁", style_table_center)
        ],
        [
            Paragraph("就诊时间", style_table_center),
            Paragraph(record['time'], style_table_center),
            Paragraph("诊断类型", style_table_center),
            Paragraph(record['type'], style_table_center),
            "", ""
        ],
        [
            Paragraph("既往病史/过敏史", style_table_center),
            Paragraph(record.get('medical_history', '无特殊既往史'), style_table_text),
            "", "", "", ""
        ]
    ]
    # 调整列宽，适配内容，避免溢出
    patient_table = Table(patient_data, colWidths=[60, 90, 40, 70, 40, 90])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_body),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightblue),
        ('BACKGROUND', (4, 0), (4, -1), colors.lightblue),
        ('SPAN', (1, 2), (-1, 2)),  # 既往病史跨列，避免溢出
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 15))

    # 3. 分诊信息表格（修复溢出）
    if triage_result:
        risk_color = {
            "低风险": colors.green,
            "中风险": colors.orange,
            "高风险": colors.red
        }.get(triage_result['risk_level'], colors.black)

        triage_data = [
            [
                Paragraph("推荐就诊科室", style_table_center),
                Paragraph(triage_result['department'], style_table_text),
                Paragraph("风险等级", style_table_center),
                Paragraph(f'<font color="{risk_color}">{triage_result["risk_level"]}</font>', style_table_center)
            ],
            [
                Paragraph("风险说明", style_table_center),
                Paragraph(triage_result['risk_desc'], style_table_text),
                "", ""
            ]
        ]
        triage_table = Table(triage_data, colWidths=[80, 220, 60, 100])
        triage_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font_body),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('SPAN', (1, 1), (-1, 1)),
        ]))
        story.append(Paragraph("一、分诊信息", style_chapter))
        story.append(triage_table)
        story.append(Spacer(1, 5))
        story.append(Paragraph(f"⚠ 就诊提醒：{triage_result['warning']}", style_body))

    # 4. 症状描述
    if 'input' in record and record['input'].strip():
        story.append(Paragraph("二、症状描述", style_chapter))
        story.append(Paragraph(clean_text(record['input']), style_body))

    # 5. AI诊断分析结果
    story.append(Paragraph("三、AI辅助诊断分析结果", style_chapter))
    result_text = clean_text(record['output'])
    paragraphs = result_text.split('\n')
    for para in paragraphs:
        para = para.strip()
        if not para:
            story.append(Spacer(1, 4))
            continue
        if re.match(r'^[0-9一二三四五六七八九十]+[.、]\s*[\u4e00-\u9fa5]{2,}', para):
            story.append(Paragraph(para, style_chapter))
        elif re.match(r'^[0-9]+[.、]\s*|^●\s*', para):
            story.append(Paragraph(para, style_list))
        else:
            story.append(Paragraph(para, style_body))

    # 6. 合规声明
    story.append(PageBreak())
    story.append(Spacer(1, A4[1] - 150))
    story.append(Paragraph("本报告仅为健康科普辅助参考，不具备法律效力，不能替代执业医师的面诊与诊断。", style_footer))
    story.append(Paragraph("身体不适请及时前往正规医院就诊，请勿根据本报告自行用药。", style_footer))

    # 生成PDF，添加页眉页脚
    def add_header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(font_title, 10)
        canvas.drawString(50, A4[1] - 40, "AI智能医疗辅助问诊系统")
        canvas.drawRightString(A4[0] - 50, A4[1] - 40, f"第 {doc.page} 页")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=60, bottomMargin=60
    )
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    buffer.seek(0)
    return buffer