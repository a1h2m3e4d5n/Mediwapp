from io import BytesIO
from pathlib import Path
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    arabic_reshaper = None
    get_display = lambda text: text


def rtl(text):
    text = str(text or '')
    if arabic_reshaper:
        return get_display(arabic_reshaper.reshape(text))
    return text


def generate_exam_pdf(exam):
    buffer = BytesIO()
    font_path = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    if font_path.exists():
        try:
            pdfmetrics.registerFont(TTFont('Arabic', str(font_path)))
            font_name = 'Arabic'
        except Exception:
            font_name = 'Helvetica'
    else:
        font_name = 'Helvetica'
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    title = ParagraphStyle('title', fontName=font_name, fontSize=18, leading=26, alignment=TA_RIGHT, textColor=colors.HexColor('#12304a'))
    body = ParagraphStyle('body', fontName=font_name, fontSize=11, leading=19, alignment=TA_RIGHT)
    small = ParagraphStyle('small', fontName=font_name, fontSize=9, leading=14, alignment=TA_RIGHT, textColor=colors.HexColor('#66788a'))
    story = [Paragraph(rtl('تقرير فحص طبي'), title), Spacer(1, 8*mm), Paragraph(rtl('MediWapp — نظام إدارة المستشفى التجريبي'), small), Spacer(1, 8*mm)]
    rows = [
        [Paragraph(rtl('المريض'), body), Paragraph(rtl(exam.patient.full_name), body)],
        [Paragraph(rtl('رقم الملف'), body), Paragraph(rtl(exam.patient.medical_record_number), body)],
        [Paragraph(rtl('رقم الهاتف'), body), Paragraph(rtl(exam.patient.phone_number), body)],
        [Paragraph(rtl('نوع الفحص'), body), Paragraph(rtl(exam.exam_type), body)],
        [Paragraph(rtl('الطبيب'), body), Paragraph(rtl(exam.physician_name or 'غير محدد'), body)],
        [Paragraph(rtl('الحالة'), body), Paragraph(rtl(exam.get_status_display()), body)],
        [Paragraph(rtl('التاريخ'), body), Paragraph(rtl(exam.created_at.strftime('%Y-%m-%d %H:%M')), body)],
    ]
    table = Table(rows, colWidths=[45*mm, 115*mm], hAlign='RIGHT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f8f6')),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#b9dcd8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#d6e8e7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story += [table, Spacer(1, 8*mm), Paragraph(rtl('ملخص النتيجة'), title), Spacer(1, 3*mm), Paragraph(rtl(exam.result_summary), body), Spacer(1, 5*mm), Paragraph(rtl('تفاصيل النتيجة'), title), Spacer(1, 3*mm), Paragraph(rtl(exam.detailed_results).replace('\n', '<br/>'), body), Spacer(1, 12*mm), Paragraph(rtl('هذا التقرير صادر من النسخة التجريبية ويحتاج إلى مراجعة الطبيب قبل اعتماده للمريض.'), small)]
    doc.build(story)
    buffer.seek(0)
    filename = f'exam-{exam.pk}-{timezone.now().strftime("%Y%m%d%H%M%S")}.pdf'
    exam.pdf_file.save(filename, ContentFile(buffer.read()), save=False)
    exam.pdf_generated_at = timezone.now()
    return exam
