"""
PDF Report Generator for RNSIT PBAS Performance Appraisal Report.
Uses ReportLab to generate a clean, official academic document.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pbas_pdf(submission):
    """
    Generates a PDF byte buffer containing the complete PBAS Performance Appraisal Report.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=1, # Center
        textColor=colors.HexColor('#0f172a')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        alignment=1, # Center
        textColor=colors.HexColor('#475569')
    )

    section_hdr_style = ParagraphStyle(
        'SecHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e3a8a')
    )

    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )

    bold_style = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0f172a')
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("RNS INSTITUTE OF TECHNOLOGY", title_style))
    elements.append(Paragraph("Channasandra, Dr. Vishnuvardhan Road, Bengaluru – 560 098", subtitle_style))
    elements.append(Paragraph("<b>PERFORMANCE BASED APPRAISAL SYSTEM (PBAS)</b> — Assistant Professor", subtitle_style))
    elements.append(Spacer(1, 10))

    # Faculty Profile Table
    profile_data = [
        [
            Paragraph("<b>Faculty Name:</b>", normal_style),
            Paragraph(submission.faculty_name, bold_style),
            Paragraph("<b>Employee ID:</b>", normal_style),
            Paragraph(submission.employee_id or "N/A", bold_style)
        ],
        [
            Paragraph("<b>Department:</b>", normal_style),
            Paragraph(submission.department, bold_style),
            Paragraph("<b>Academic Year:</b>", normal_style),
            Paragraph(submission.academic_year, bold_style)
        ],
        [
            Paragraph("<b>Appraisal Period:</b>", normal_style),
            Paragraph("April 2026 – March 2027", normal_style),
            Paragraph("<b>Appraisal Status:</b>", normal_style),
            Paragraph(submission.status, bold_style)
        ]
    ]
    t_profile = Table(profile_data, colWidths=[1.3*inch, 2.3*inch, 1.3*inch, 2.3*inch])
    t_profile.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_profile)
    elements.append(Spacer(1, 12))

    # Score Summary Table
    elements.append(Paragraph("1. Summary of Appraisal Scores & Scaling", section_hdr_style))
    elements.append(Spacer(1, 4))

    score_table_data = [
        [
            Paragraph("<b>Assessment Section / Component</b>", bold_style),
            Paragraph("<b>Max Marks</b>", bold_style),
            Paragraph("<b>Marks Claimed / Verified</b>", bold_style)
        ],
        [
            Paragraph("Section I: Teaching Learning Process (Course Feedback, Results & TLP)", normal_style),
            Paragraph("70", normal_style),
            Paragraph(f"<b>{submission.section1_final_score}</b>", normal_style)
        ],
        [
            Paragraph("Section II: Research & Development and Consultancy Work", normal_style),
            Paragraph("40", normal_style),
            Paragraph(f"<b>{submission.section2_final_score}</b>", normal_style)
        ],
        [
            Paragraph("Section III: Technical & Professional Activities", normal_style),
            Paragraph("20", normal_style),
            Paragraph(f"<b>{submission.section3_final_score}</b>", normal_style)
        ],
        [
            Paragraph("<b>Subtotal (Section I + II + III)</b>", bold_style),
            Paragraph("<b>130</b>", bold_style),
            Paragraph(f"<b>{submission.subtotal_130}</b>", bold_style)
        ],
        [
            Paragraph("<b>Scaled Score [(Subtotal ÷ 130) × 80]</b>", bold_style),
            Paragraph("<b>80</b>", bold_style),
            Paragraph(f"<b>{submission.scaled_80}</b>", bold_style)
        ],
        [
            Paragraph("Section IV: Academic Administration Activities", normal_style),
            Paragraph("20", normal_style),
            Paragraph(f"<b>{submission.section4_final_score}</b>", normal_style)
        ],
        [
            Paragraph("HOD Evaluation (5 Departmental Criteria, 3 marks each)", normal_style),
            Paragraph("15", normal_style),
            Paragraph(f"<b>{submission.hod_score}</b>", normal_style)
        ],
        [
            Paragraph("Principal Evaluation (5 Institutional Criteria, 1 mark each)", normal_style),
            Paragraph("05", normal_style),
            Paragraph(f"<b>{submission.principal_score}</b>", normal_style)
        ],
        [
            Paragraph("<b>FINAL APPRAISAL SCORE (Scaled 80 + HOD 15 + Principal 5)</b>", bold_style),
            Paragraph("<b>100</b>", bold_style),
            Paragraph(f"<b><font color='#1e3a8a' size='+1'>{submission.grand_total_100}</font> / 100</b>", bold_style)
        ],
        [
            Paragraph("<b>FINAL PERFORMANCE GRADE</b>", bold_style),
            Paragraph("<b>Scale</b>", bold_style),
            Paragraph(f"<b><font color='#059669' size='+1'>{submission.performance_grade}</font></b>", bold_style)
        ]
    ]

    t_scores = Table(score_table_data, colWidths=[4.2*inch, 1.2*inch, 1.8*inch])
    t_scores.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,4), (-1,5), colors.HexColor('#f1f5f9')),
        ('BACKGROUND', (0,9), (-1,10), colors.HexColor('#fef3c7')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (1,0), (2,-1), 'CENTER'),
    ]))
    elements.append(t_scores)
    elements.append(Spacer(1, 14))

    # Grade Legend Table
    elements.append(Paragraph("2. Official Performance Grading Rubric", section_hdr_style))
    elements.append(Spacer(1, 4))
    rubric_data = [
        [Paragraph("<b>Grade Band</b>", bold_style), Paragraph("<b>Score Range</b>", bold_style), Paragraph("<b>Recommendation Outcome</b>", bold_style)],
        [Paragraph("Excellent", normal_style), Paragraph("91 – 100", normal_style), Paragraph("Recommended for Merit & Annual Increment", normal_style)],
        [Paragraph("Very Good", normal_style), Paragraph("81 – 90", normal_style), Paragraph("Recommended for Annual Increment", normal_style)],
        [Paragraph("Good", normal_style), Paragraph("71 – 80", normal_style), Paragraph("Recommended for Annual Increment", normal_style)],
        [Paragraph("Average", normal_style), Paragraph("61 – 70", normal_style), Paragraph("Annual Increment with Specific Improvement Goals", normal_style)],
        [Paragraph("Not Satisfactory", normal_style), Paragraph("60 and below", normal_style), Paragraph("Increment Subject to Review / Development Plan", normal_style)],
    ]
    t_rubric = Table(rubric_data, colWidths=[1.8*inch, 1.8*inch, 3.6*inch])
    t_rubric.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ]))
    elements.append(t_rubric)
    elements.append(Spacer(1, 25))

    # Signatures & Certifications Block
    sig_data = [
        [
            Paragraph("<b>Signature of Faculty Member</b><br/><br/><br/>Date: ________________", normal_style),
            Paragraph("<b>Signature of Head of Department</b><br/><br/><br/>Date: ________________", normal_style),
            Paragraph("<b>Signature of Principal</b><br/><br/><br/>Date: ________________", normal_style)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[2.4*inch, 2.4*inch, 2.4*inch])
    t_sig.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    elements.append(t_sig)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
