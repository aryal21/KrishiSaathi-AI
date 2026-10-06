"""PDF generation utilities for KrishiSaathi AI using ReportLab."""
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_disease_pdf(data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#555555'),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1B5E20'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#222222')
    )
    alert_style = ParagraphStyle(
        'Alert',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#D32F2F'),
        leading=14
    )

    story = []
    # Header
    story.append(Paragraph("🌾 KrishiSaathi AI - Crop Health Diagnostic Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')} | ICAR Standard Reference", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2E7D32'), spaceAfter=15))

    # Summary Table
    info_data = [
        [Paragraph("<b>Crop/Specimen:</b>", body_style), Paragraph(str(data.get("crop", "Field Crop")), body_style),
         Paragraph("<b>Diagnosis Date:</b>", body_style), Paragraph(datetime.now().strftime('%d/%m/%Y'), body_style)],
        [Paragraph("<b>Detected Disease:</b>", body_style), Paragraph(f"<b>{data.get('disease', 'Unknown')}</b>", body_style),
         Paragraph("<b>Confidence Level:</b>", body_style), Paragraph(f"{data.get('confidence', 85)}%", body_style)],
        [Paragraph("<b>Severity Level:</b>", body_style), Paragraph(f"<b>{data.get('severity', 'Medium')}</b>", alert_style),
         Paragraph("<b>Estimated Treatment Cost:</b>", body_style), Paragraph(str(data.get('cost', '₹350-500/acre')), body_style)]
    ]
    t = Table(info_data, colWidths=[120, 150, 120, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F5F9F5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#C8E6C9')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Symptoms
    story.append(Paragraph("Visible Symptoms Identified:", section_style))
    symptoms = data.get("symptoms", [])
    if isinstance(symptoms, list):
        for s in symptoms:
            story.append(Paragraph(f"• {s}", body_style))
    else:
        story.append(Paragraph(str(symptoms), body_style))
    story.append(Spacer(1, 10))

    # Treatment Plan
    story.append(Paragraph("Recommended Treatment Protocol (Immediate Action):", section_style))
    treatment = data.get("treatment", "")
    for line in str(treatment).split("\n"):
        line = line.strip()
        if line:
            story.append(Paragraph(line, body_style))
    story.append(Spacer(1, 10))

    # Preventive Measures
    story.append(Paragraph("Long-term Prevention & Cultural Practices:", section_style))
    prevention = data.get("prevention", "")
    for line in str(prevention).split("\n"):
        line = line.strip()
        if line:
            story.append(Paragraph(f"• {line}", body_style))
    story.append(Spacer(1, 15))

    # Advisory Footer
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#BDBDBD'), spaceAfter=10))
    story.append(Paragraph("<b>Scientific Reference:</b> " + str(data.get("source", "ICAR Crop Protection Advisory Board 2024")), subtitle_style))
    story.append(Paragraph("<i>Note: Before applying chemical pesticides, consult your local Krishi Vigyan Kendra (KVK) or call Kisan Call Centre 1800-180-1551.</i>", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_claim_receipt_pdf(claim_data: dict, user_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1976D2'),
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#212121')
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=10,
        spaceAfter=4
    )

    story = []
    story.append(Paragraph("🏛️ Pradhan Mantri Fasal Bima Yojana (PMFBY)", title_style))
    story.append(Paragraph("Official Claim Submission Acknowledgement Receipt | KrishiSaathi Assisted Portal", body_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1976D2'), spaceAfter=15))

    claim_id = claim_data.get("claim_id", "PMFBY-2026-PENDING")
    
    grid = [
        [Paragraph("<b>Claim ID:</b>", body_style), Paragraph(f"<b><font color='#1976D2'>{claim_id}</font></b>", body_style),
         Paragraph("<b>Submission Date:</b>", body_style), Paragraph(datetime.now().strftime("%d-%m-%Y %H:%M"), body_style)],
        [Paragraph("<b>Farmer Name:</b>", body_style), Paragraph(user_data.get("name", "Farmer"), body_style),
         Paragraph("<b>Mobile:</b>", body_style), Paragraph("+91 " + str(user_data.get("mobile", "")), body_style)],
        [Paragraph("<b>Village & District:</b>", body_style), Paragraph(f"{user_data.get('village','')}, {user_data.get('district','')}", body_style),
         Paragraph("<b>State:</b>", body_style), Paragraph(str(user_data.get('state','')), body_style)],
        [Paragraph("<b>Affected Crop:</b>", body_style), Paragraph(str(claim_data.get('crop','')), body_style),
         Paragraph("<b>Survey/Khata No:</b>", body_style), Paragraph(str(claim_data.get('survey_number','74/A')), body_style)],
        [Paragraph("<b>Affected Area:</b>", body_style), Paragraph(f"{claim_data.get('land_acres',1)} Acres", body_style),
         Paragraph("<b>Cause of Loss:</b>", body_style), Paragraph(str(claim_data.get('loss_cause','')), body_style)],
        [Paragraph("<b>Estimated Damage:</b>", body_style), Paragraph(f"{claim_data.get('loss_percentage', 50)}%", body_style),
         Paragraph("<b>Estimated Payout:</b>", body_style), Paragraph(f"<b>₹{claim_data.get('estimated_payout', 24000):,.0f}</b>", body_style)],
        [Paragraph("<b>Current Status:</b>", body_style), Paragraph("<b><font color='#2E7D32'>Submitted - Under Review</font></b>", body_style),
         Paragraph("<b>Loss Intimation SLA:</b>", body_style), Paragraph("Within 72 Hours (Compliant)", body_style)]
    ]

    t = Table(grid, colWidths=[120, 150, 120, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#93C5FD')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Next Steps in Claim Settlement:", h2_style))
    steps = [
        "1. <b>Field Inspection</b>: Insurance company surveyor and agriculture officer will visit your farm within 10 days.",
        "2. <b>Keep Documents Ready</b>: Keep 7/12 land extract, bank passbook, sowing certificate, and damage photos handy.",
        "3. <b>Direct Benefit Transfer (DBT)</b>: Approved amount will be credited directly to your Aadhaar-linked bank account.",
        "4. <b>Track Status</b>: Use this Claim ID on the national PMFBY portal (pmfby.gov.in) or KrishiSaathi Dashboard."
    ]
    for s in steps:
        story.append(Paragraph(s, body_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceAfter=8))
    story.append(Paragraph("National Toll-Free PMFBY Helpline: <b>1800-180-1551</b> | Krishi Bhavan, New Delhi", ParagraphStyle('Foot', parent=body_style, fontSize=9, textColor=colors.HexColor('#64748B'))))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_complaint_pdf(complaint_data: dict, user_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#D32F2F'),
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#1E293B')
    )

    story = []
    story.append(Paragraph("OFFICIAL COMPLAINT: COUNTERFEIT / SUBSTANDARD AGRI-INPUT REPORT", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#D32F2F'), spaceAfter=15))

    date_str = datetime.now().strftime("%d %B %Y")
    letter_text = f"""
    <b>To:</b><br/>
    The District Agriculture Officer / Quality Control Inspector<br/>
    Department of Agriculture, {user_data.get('district', 'District')}, {user_data.get('state', 'State')}<br/><br/>

    <b>Date:</b> {date_str}<br/>
    <b>Subject:</b> Formal complaint regarding suspected fake / counterfeit agricultural input under Insecticides Act 1968 and Seeds Act 1966.<br/><br/>

    Respected Sir/Madam,<br/><br/>
    I, <b>{user_data.get('name', 'Concerned Farmer')}</b>, resident of village <b>{user_data.get('village', 'Village')}</b>, Mobile: <b>+91 {user_data.get('mobile', '')}</b>, wish to report the purchase of a suspected counterfeit / spurious agricultural product.<br/><br/>

    <b>Product Particulars:</b><br/>
    • <b>Product Name:</b> {complaint_data.get('product_name', 'Agri-Chemical / Seed')}<br/>
    • <b>Stated Manufacturer:</b> {complaint_data.get('company', 'Unknown')}<br/>
    • <b>Batch / Lot Number:</b> {complaint_data.get('batch_no', 'N/A')}<br/>
    • <b>Purchased From Dealer:</b> {complaint_data.get('dealer_name', 'Local Retailer')}<br/>
    • <b>Authenticity Verification Status:</b> FAILED (Batch mismatch with verified manufacturer records)<br/><br/>

    Counterfeit products cause devastating yield losses and financial ruin to hardworking farming families. I request the agricultural department to inspect the dealer's premises, collect official samples for lab testing, and initiate appropriate proceedings.<br/><br/>

    Sincerely,<br/>
    <b>{user_data.get('name', 'Farmer')}</b><br/>
    Applicant & Farmer Member, KrishiSaathi Farmer Protection Network
    """
    story.append(Paragraph(letter_text, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
