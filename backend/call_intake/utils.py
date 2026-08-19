import os
from io import BytesIO
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_intake_pdf(session):
    """
    Generates a professional PDF summary of the voice intake.
    Handles native scripts (Hindi/Kannada/Tamil) via Noto Sans.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50,
    )
    styles = getSampleStyleSheet()

    # Register NotoSans for Multilingual support
    font_paths = [
        settings.BASE_DIR / 'static' / 'fonts' / 'NotoSans-Regular.ttf',
        settings.BASE_DIR.parent / 'frontend_mobile' / 'assets' / 'fonts' / 'NotoSans-Regular.ttf',
    ]
    font_name = 'Helvetica'
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont('NotoSans', str(fp)))
                font_name = 'NotoSans'
                break
            except Exception:
                continue

    # --- Styles ---
    title_style = ParagraphStyle(
        'Title', fontName=font_name, fontSize=20, leading=24,
        spaceAfter=6, textColor=colors.HexColor("#1565C0"),
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', fontName=font_name, fontSize=10, leading=14,
        spaceAfter=20, textColor=colors.HexColor("#666666"),
    )
    section_style = ParagraphStyle(
        'Section', fontName=font_name, fontSize=13, leading=16,
        spaceBefore=16, spaceAfter=8, textColor=colors.HexColor("#1565C0"),
        borderWidth=0, borderPadding=0,
    )
    label_style = ParagraphStyle(
        'Label', fontName=font_name, fontSize=10, leading=12,
        textColor=colors.HexColor("#1565C0"),
    )
    body_style = ParagraphStyle(
        'Body', fontName=font_name, fontSize=10, leading=14,
        spaceAfter=4,
    )
    value_style = ParagraphStyle(
        'Value', fontName=font_name, fontSize=10, leading=14,
    )
    footer_style = ParagraphStyle(
        'Footer', fontName=font_name, fontSize=8, leading=10,
        textColor=colors.HexColor("#999999"), alignment=1,
    )
    small_style = ParagraphStyle(
        'Small', fontName=font_name, fontSize=8, leading=10,
        textColor=colors.HexColor("#888888"),
    )

    elements = []

    # === Header: Logo + Title ===
    logo_path = os.path.join(settings.BASE_DIR, 'media', 'jobcare_logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=40*mm, height=15*mm)
        img.hAlign = 'LEFT'
        elements.append(img)
        elements.append(Spacer(1, 4))

    elements.append(Paragraph("Voice Intake Summary", title_style))
    elements.append(Paragraph(f"Session ID: {session.id}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1565C0"), spaceAfter=12))

    # === Section 1: Candidate Info ===
    answers = list(session.answers.select_related('question').all().order_by('question__order'))
    answers_by_key = {a.question.question_key: a for a in answers}

    candidate_name = answers_by_key.get('name')
    candidate_phone = session.phone_number
    candidate_email = session.email or '—'

    elements.append(Paragraph("Candidate Information", section_style))
    info_data = [
        [Paragraph("Name", label_style), Paragraph(candidate_name.answer_text if candidate_name else '—', value_style)],
        [Paragraph("Phone", label_style), Paragraph(candidate_phone, value_style)],
        [Paragraph("Email", label_style), Paragraph(candidate_email, value_style)],
        [Paragraph("Date & Time", label_style),
         Paragraph(session.completed_at.strftime("%d %b %Y, %I:%M %p") if session.completed_at
                   else session.started_at.strftime("%d %b %Y, %I:%M %p"), value_style)],
        [Paragraph("Language", label_style), Paragraph(session.get_language_display(), value_style)],
    ]
    t = Table(info_data, colWidths=[100, 380])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 16))

    # === Section 2: Intake Questions & Answers ===
    elements.append(Paragraph("Intake Details", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E0E0E0"), spaceAfter=8))

    for ans in answers:
        q_key = ans.question.question_key
        confirmation = " ✓" if ans.confirmed else ""
        elements.append(Paragraph(
            f"<b>{ans.question.question_text_en}</b>{confirmation}",
            label_style,
        ))
        elements.append(Paragraph(f"{ans.answer_text}", body_style))
        elements.append(Spacer(1, 10))

    # === Section 3: AI Summary (if available) ===
    if session.ai_summary:
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1565C0"), spaceAfter=8))
        elements.append(Paragraph("AI Summary", section_style))
        elements.append(Paragraph(session.ai_summary, body_style))
        elements.append(Spacer(1, 8))

    # === Section 4: Profile Data (if available) ===
    if session.profile_data and not isinstance(session.profile_data, dict) or (
        isinstance(session.profile_data, dict) and session.profile_data
    ):
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1565C0"), spaceAfter=8))
        elements.append(Paragraph("Extracted Profile", section_style))
        profile_items = []
        if isinstance(session.profile_data, dict):
            for key, val in session.profile_data.items():
                profile_items.append([
                    Paragraph(f"<b>{key.replace('_', ' ').title()}</b>", label_style),
                    Paragraph(str(val), value_style),
                ])
        if profile_items:
            pt = Table(profile_items, colWidths=[140, 340])
            pt.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
            ]))
            elements.append(pt)

    # === Footer ===
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=6))
    elements.append(Paragraph(
        f"Generated by JobCare on {datetime.now().strftime('%d %b %Y at %I:%M %p')}",
        footer_style,
    ))
    elements.append(Paragraph(
        f"JobCare Voice — India's first AI voice job platform for workers",
        small_style,
    ))

    doc.build(elements)

    filename = (
        f"intake_{session.phone_number}_"
        f"{session.started_at.strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    session.pdf_file.save(filename, ContentFile(buffer.getvalue()), save=False)
    buffer.close()
