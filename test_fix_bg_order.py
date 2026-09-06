import os
import io
import uuid
import qrcode
import pypdfium2
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

W, H = landscape(letter)  # 792 x 612

def _draw_ornament(c, x, y, size=10):
    c.saveState()
    c.setFillColor(colors.HexColor('#D97706'))
    path = c.beginPath()
    path.moveTo(x, y + size / 2)
    path.lineTo(x + size / 2, y)
    path.lineTo(x, y - size / 2)
    path.lineTo(x - size / 2, y)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    c.restoreState()

def draw_background(c, doc):
    c.saveState()

    # 1. Warm Off-White / Cream background FIRST
    c.setFillColor(colors.HexColor('#FAF9F5'))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # 2. Top-Right Corner Curved Navy Ribbon Arc
    path_tr = c.beginPath()
    path_tr.moveTo(W - 220, H)
    path_tr.curveTo(W - 100, H, W, H - 100, W, H - 220)
    path_tr.lineTo(W, H)
    path_tr.close()
    c.setFillColor(colors.HexColor('#0B1B3D'))
    c.drawPath(path_tr, fill=1, stroke=0)

    # Gold Ribbon Accent Stripe Top-Right
    path_tr_gold = c.beginPath()
    path_tr_gold.moveTo(W - 235, H)
    path_tr_gold.curveTo(W - 110, H, W, H - 110, W, H - 235)
    path_tr_gold.lineTo(W - 220, H)
    path_tr_gold.curveTo(W - 100, H, W, H - 100, W, H - 220)
    path_tr_gold.close()
    c.setFillColor(colors.HexColor('#D97706'))
    c.drawPath(path_tr_gold, fill=1, stroke=0)

    # 3. Bottom-Left Corner Curved Navy Ribbon Arc
    path_bl = c.beginPath()
    path_bl.moveTo(0, 220)
    path_bl.curveTo(0, 100, 100, 0, 220, 0)
    path_bl.lineTo(0, 0)
    path_bl.close()
    c.setFillColor(colors.HexColor('#0B1B3D'))
    c.drawPath(path_bl, fill=1, stroke=0)

    # Gold Ribbon Accent Stripe Bottom-Left
    path_bl_gold = c.beginPath()
    path_bl_gold.moveTo(0, 235)
    path_bl_gold.curveTo(0, 110, 110, 0, 235, 0)
    path_bl_gold.lineTo(220, 0)
    path_bl_gold.curveTo(100, 0, 0, 100, 0, 220)
    path_bl_gold.close()
    c.setFillColor(colors.HexColor('#D97706'))
    c.drawPath(path_bl_gold, fill=1, stroke=0)

    # 4. Outer Gold Border & Inner Navy Border
    c.setStrokeColor(colors.HexColor('#D97706'))
    c.setLineWidth(1.8)
    c.rect(16, 16, W - 32, H - 32)

    c.setStrokeColor(colors.HexColor('#0B1B3D'))
    c.setLineWidth(0.8)
    c.rect(22, 22, W - 44, H - 44)

    # Corner Ornaments
    _draw_ornament(c, 22, 22, size=10)
    _draw_ornament(c, W - 22, 22, size=10)
    _draw_ornament(c, 22, H - 22, size=10)
    _draw_ornament(c, W - 22, H - 22, size=10)

    # 5. Top-Left Logo & Branding
    c.setFillColor(colors.HexColor('#0B1B3D'))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(42, H - 58, "SJ TECH")
    c.setFillColor(colors.HexColor('#D97706'))
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(42, H - 72, "— CLASSES —")
    c.setFillColor(colors.HexColor('#475569'))
    c.setFont("Helvetica", 7.5)
    c.drawString(42, H - 83, "Learn Today, Build Tomorrow")

    # 6. Left Sidebar Feature Bullets (5 Items)
    features = [
        ("EXPERT FACULTY", H - 145),
        ("PRACTICAL LEARNING", H - 185),
        ("REAL WORLD PROJECTS", H - 225),
        ("QUALITY EDUCATION", H - 265),
        ("INTERNSHIP & PLACEMENT SUPPORT", H - 305),
    ]
    for title, y_pos in features:
        c.setStrokeColor(colors.HexColor('#D97706'))
        c.setLineWidth(0.8)
        c.setFillColor(colors.HexColor('#FFFBEB'))
        c.roundRect(42, y_pos - 4, 18, 16, 3, fill=1, stroke=1)
        
        c.setFillColor(colors.HexColor('#D97706'))
        c.circle(51, y_pos + 4, 2, fill=1, stroke=0)

        c.setFillColor(colors.HexColor('#0B1B3D'))
        c.setFont("Helvetica-Bold", 6.2)
        c.drawString(66, y_pos + 2, title)

        c.setStrokeColor(colors.HexColor('#E2E8F0'))
        c.setLineWidth(0.5)
        c.line(42, y_pos - 9, 168, y_pos - 9)

    # 7. Top-Right 3D Medal Ribbon Seal
    seal_path = os.path.join('courses', 'static', 'courses', 'images', 'certificate_seal.jpg')
    if os.path.exists(seal_path):
        c.drawImage(seal_path, W - 150, H - 165, width=110, height=130, mask='auto')

    # 8. Bottom Left Circular Stamp (ESTD 2020)
    c.setStrokeColor(colors.HexColor('#0B1B3D'))
    c.setLineWidth(1.4)
    c.circle(230, 75, 26, fill=0, stroke=1)
    c.setLineWidth(0.6)
    c.circle(230, 75, 22, fill=0, stroke=1)
    c.setFillColor(colors.HexColor('#0B1B3D'))
    c.setFont("Helvetica-Bold", 5.8)
    c.drawCentredString(230, 88, "SJ TECH CLASSES")
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(230, 80, "* ESTD. 2020 *")
    c.setFont("Helvetica", 5)
    c.drawCentredString(230, 70, "SOLAPUR")

    # 9. Bottom Dark Navy Banner
    c.setFillColor(colors.HexColor('#0B1B3D'))
    path_b = c.beginPath()
    path_b.moveTo(W/2 - 160, 14)
    path_b.lineTo(W/2 + 160, 14)
    path_b.lineTo(W/2 + 150, 32)
    path_b.lineTo(W/2 - 150, 32)
    path_b.close()
    c.drawPath(path_b, fill=1, stroke=0)

    c.setFillColor(colors.HexColor('#F59E0B'))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(W / 2, 20, "*   KEEP LEARNING, KEEP GROWING, KEEP ACHIEVING!   *")

    c.restoreState()

buffer = io.BytesIO()
doc = SimpleDocTemplate(
    buffer,
    pagesize=landscape(letter),
    rightMargin=0.65 * inch,
    leftMargin=2.0 * inch,
    topMargin=0.35 * inch,
    bottomMargin=0.35 * inch,
)

story = []
styles = getSampleStyleSheet()

# QR Code
qr = qrcode.QRCode(version=1, box_size=2, border=1)
qr.add_data("http://127.0.0.1:8000/certificate/1/verify/")
qr.make(fit=True)
qr_img = qr.make_image(fill_color="#0B1B3D", back_color="white")
qr_buf = io.BytesIO()
qr_img.save(qr_buf, format="PNG")
qr_buf.seek(0)
qr_reportlab = Image(qr_buf, width=0.68 * inch, height=0.68 * inch)

# Signature
sig_path = os.path.join('courses', 'static', 'courses', 'images', 'sunny_signature.jpg')
sig_img = Image(sig_path, width=1.4 * inch, height=0.45 * inch) if os.path.exists(sig_path) else None

# Styles
flourish_s = ParagraphStyle('FS', parent=styles['Normal'], fontName='Times-Italic', fontSize=12, textColor=colors.HexColor('#D97706'), alignment=1, spaceAfter=1)
cert_title_s = ParagraphStyle('CT', parent=styles['Heading1'], fontName='Times-Bold', fontSize=28, textColor=colors.HexColor('#0B1B3D'), alignment=1, spaceAfter=1, leading=30)
sub_title_s = ParagraphStyle('ST', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor('#D97706'), alignment=1, spaceAfter=4)
certify_banner_s = ParagraphStyle('CBS', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white, alignment=1)
name_s = ParagraphStyle('NS', parent=styles['Heading1'], fontName='Times-BoldItalic', fontSize=30, textColor=colors.HexColor('#0B1B3D'), alignment=1, spaceAfter=1, leading=32)
course_label_s = ParagraphStyle('CLS', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=2)
course_name_s = ParagraphStyle('CNS', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#0B1B3D'), alignment=1, spaceAfter=3, leading=15)
conducted_s = ParagraphStyle('CS', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor('#0B1B3D'), alignment=1, spaceAfter=1)
desc_s = ParagraphStyle('DS', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=6, leading=10)
meta_label_s = ParagraphStyle('MLS', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=5.5, textColor=colors.HexColor('#64748B'), alignment=1)
meta_val_s = ParagraphStyle('MVS', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.HexColor('#0B1B3D'), alignment=1)
sign_name_s = ParagraphStyle('SNS', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#0B1B3D'), alignment=1)
sign_title_s = ParagraphStyle('STS', parent=styles['Normal'], fontName='Helvetica', fontSize=6.5, textColor=colors.HexColor('#64748B'), alignment=1)

story.append(Paragraph("---   ~   ---", flourish_s))
story.append(Paragraph("CERTIFICATE", cert_title_s))
story.append(Paragraph("— OF COMPLETION —", sub_title_s))

cert_banner_table = Table([[Paragraph("THIS IS TO CERTIFY THAT", certify_banner_s)]], colWidths=[2.4 * inch])
cert_banner_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0B1B3D')),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))
story.append(cert_banner_table)
story.append(Spacer(1, 0.04 * inch))

story.append(Paragraph("Rahul Patil", name_s))
story.append(HRFlowable(width="40%", thickness=1, color=colors.HexColor('#D97706'), spaceAfter=4))

story.append(Paragraph("has successfully completed the course", course_label_s))
story.append(Paragraph("—  PYTHON PROGRAMMING WITH DJANGO  —", course_name_s))
story.append(Paragraph("conducted by <b>SJ Tech Classes.</b>", conducted_s))
story.append(Paragraph(
    "We appreciate the dedication, hard work and commitment<br/>shown by the student during the course.",
    desc_s
))

meta_table = Table([
    [Paragraph("COURSE DURATION", meta_label_s), Paragraph("FROM", meta_label_s), Paragraph("TO", meta_label_s)],
    [Paragraph("40 HOURS", meta_val_s), Paragraph("01 JUNE 2026", meta_val_s), Paragraph("30 JULY 2026", meta_val_s)]
], colWidths=[1.4 * inch, 1.5 * inch, 1.5 * inch])
meta_table.setStyle(TableStyle([
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 2),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ('LINEAFTER', (0, 0), (0, -1), 0.5, colors.HexColor('#CBD5E1')),
    ('LINEAFTER', (1, 0), (1, -1), 0.5, colors.HexColor('#CBD5E1')),
]))
story.append(meta_table)
story.append(Spacer(1, 0.05 * inch))

sig_rows = [[sig_img]] if sig_img else [[Spacer(1, 0.35 * inch)]]
sig_rows.append([HRFlowable(width="85%", thickness=0.8, color=colors.HexColor('#0B1B3D'))])
sig_rows.append([Paragraph("SUNNY SIR", sign_name_s)])
sig_rows.append([Paragraph("FOUNDER &amp; INSTRUCTOR", sign_title_s)])
sig_rows.append([Paragraph("SJ TECH CLASSES", sign_title_s)])
sig_block = Table(sig_rows, colWidths=[2.0 * inch])
sig_block.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1)]))

right_box = Table([
    [Paragraph("CERTIFICATE ID", meta_label_s)],
    [Paragraph("SJTC2026P041", meta_val_s)],
    [Spacer(1, 1)],
    [qr_reportlab],
    [Paragraph("Scan to Verify", ParagraphStyle('tiny', parent=styles['Normal'], fontSize=6, alignment=1, textColor=colors.HexColor('#475569')))],
], colWidths=[1.3 * inch])
right_box.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1)]))

footer_table = Table([[Spacer(1.1 * inch, 0.5 * inch), sig_block, right_box]], colWidths=[1.2 * inch, 2.1 * inch, 1.3 * inch])
footer_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'BOTTOM')]))
story.append(footer_table)

# Build with onFirstPage=draw_background so background is drawn BEFORE story!
doc.build(story, onFirstPage=draw_background)
buffer.seek(0)

# Render to test PNG
pdf = pypdfium2.PdfDocument(buffer.getvalue())
img = pdf[0].render(scale=3).to_pil()
artifact_path = r'C:\Users\User\.gemini\antigravity\brain\cb3e547d-a934-4b82-9e81-71668e9248cb\perfect_cert_test.png'
img.save(artifact_path)
print("SUCCESS! Rendered perfect_cert_test.png at:", artifact_path)
