import os
import uuid
import qrcode
import io
from django.conf import settings
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.core.files.base import ContentFile
from reportlab.graphics.shapes import Drawing, Circle, String, Polygon, Line


def can_generate_certificate(enrollment):
    from courses.models import Quiz, QuizAttempt
    if enrollment.progress_percentage < 100:
        return False, "Course progress is not 100% complete."
    quizzes = Quiz.objects.filter(lesson__module__course=enrollment.course)
    for quiz in quizzes:
        passed_attempt = QuizAttempt.objects.filter(
            quiz=quiz, student=enrollment.student, passed=True
        ).exists()
        if not passed_attempt:
            return False, f"Quiz '{quiz.title}' has not been passed yet."
    return True, "Eligible"


def _draw_ornament(c, x, y, size=10):
    """Draw a decorative gold diamond ornament."""
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


def draw_certificate_background(c, doc):
    """
    Draws canvas background decorations FIRST before story flowables are rendered.
    All fonts increased by an additional +2pt (total +4pt boost).
    """
    W, H = landscape(letter)  # 792 x 612
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

    # 5. Top-Left Logo & Branding (+4pt total)
    c.setFillColor(colors.HexColor('#0B1B3D'))
    c.setFont("Helvetica-Bold", 28)
    c.drawString(36, H - 56, "SJ TECH")
    c.setFillColor(colors.HexColor('#D97706'))
    c.setFont("Helvetica-Bold", 15.5)
    c.drawString(36, H - 74, "— CLASSES —")
    c.setFillColor(colors.HexColor('#475569'))
    c.setFont("Helvetica", 11.5)
    c.drawString(36, H - 90, "Learn Today, Build Tomorrow")

    # 6. Left Sidebar Feature Bullets (5 Items) (+4pt total)
    features = [
        ("EXPERT FACULTY", H - 148),
        ("PRACTICAL LEARNING", H - 188),
        ("REAL WORLD PROJECTS", H - 228),
        ("QUALITY EDUCATION", H - 268),
        ("INTERNSHIP & PLACEMENT SUPPORT", H - 308),
    ]
    for title, y_pos in features:
        c.setStrokeColor(colors.HexColor('#D97706'))
        c.setLineWidth(0.8)
        c.setFillColor(colors.HexColor('#FFFBEB'))
        c.roundRect(36, y_pos - 4, 18, 16, 3, fill=1, stroke=1)
        
        c.setFillColor(colors.HexColor('#D97706'))
        c.circle(45, y_pos + 4, 2.4, fill=1, stroke=0)

        c.setFillColor(colors.HexColor('#0B1B3D'))
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(59, y_pos + 1, title)

        c.setStrokeColor(colors.HexColor('#E2E8F0'))
        c.setLineWidth(0.5)
        c.line(36, y_pos - 9, 182, y_pos - 9)

    # 7. Top-Right 3D Medal Ribbon Seal
    seal_path = os.path.join(settings.BASE_DIR, 'courses', 'static', 'courses', 'images', 'certificate_seal.jpg')
    if os.path.exists(seal_path):
        c.drawImage(seal_path, W - 150, H - 165, width=110, height=130, mask='auto')

    # 8. Bottom Dark Navy Banner (+4pt total)
    c.setFillColor(colors.HexColor('#0B1B3D'))
    path_b = c.beginPath()
    path_b.moveTo(W/2 - 190, 14)
    path_b.lineTo(W/2 + 190, 14)
    path_b.lineTo(W/2 + 180, 36)
    path_b.lineTo(W/2 - 180, 36)
    path_b.close()
    c.drawPath(path_b, fill=1, stroke=0)

    c.setFillColor(colors.HexColor('#F59E0B'))
    c.setFont("Helvetica-Bold", 12.0)
    c.drawCentredString(W / 2, 21, "*   KEEP LEARNING, KEEP GROWING, KEEP ACHIEVING!   *")

    c.restoreState()


def create_stamp_drawing():
    """Generates the circular official stamp directly as a Flowable Drawing with centered Graduation Cap Logo."""
    # Stamp width & height 90x90
    d = Drawing(90, 90)
    
    # Outer circle
    d.add(Circle(45, 45, 42, fillColor=colors.HexColor('#FFFBEB'), strokeColor=colors.HexColor('#0B1B3D'), strokeWidth=1.5))
    
    # Inner circle
    d.add(Circle(45, 45, 37, fillColor=None, strokeColor=colors.HexColor('#0B1B3D'), strokeWidth=0.6))
    
    # Vector Graduation Cap Logo (Emblem) in center
    # Diamond Cap Top
    d.add(Polygon([45, 52, 55, 48, 45, 44, 35, 48], fillColor=colors.HexColor('#0B1B3D'), strokeColor=colors.HexColor('#0B1B3D'), strokeWidth=0.5))
    # Cap Base
    d.add(Polygon([39, 45, 39, 42, 45, 40, 51, 42, 51, 45], fillColor=colors.HexColor('#0B1B3D'), strokeColor=colors.HexColor('#0B1B3D'), strokeWidth=0.5))
    # Tassel
    d.add(Line(45, 48, 34, 45, strokeColor=colors.HexColor('#D97706'), strokeWidth=0.8))
    d.add(Circle(34, 45, 1.2, fillColor=colors.HexColor('#D97706'), strokeColor=None))

    # Stamp Texts
    d.add(String(45, 62, "SJ TECH", textAnchor='middle', fontName='Helvetica-Bold', fontSize=8.5, fillColor=colors.HexColor('#0B1B3D')))
    d.add(String(45, 28, "CLASSES", textAnchor='middle', fontName='Helvetica-Bold', fontSize=8.5, fillColor=colors.HexColor('#0B1B3D')))
    d.add(String(45, 18, "* ESTD. 2020 *", textAnchor='middle', fontName='Helvetica-Bold', fontSize=6.5, fillColor=colors.HexColor('#0B1B3D')))
    d.add(String(45, 9, "SOLAPUR", textAnchor='middle', fontName='Helvetica', fontSize=6.5, fillColor=colors.HexColor('#0B1B3D')))
    
    return d


def generate_pdf_certificate(enrollment, force=False, notify_student=True):
    """
    Generates a single-page extra-large PDF certificate for SJ Tech Classes (+4pt total font boost).
    Includes the vector graduation cap logo directly inside the circular stamp in the bottom left column.
    Uses admin-edited custom certificate fields (student_name, course_title, dates, duration, instructor).
    """
    from courses.models import Certificate

    # Gracefully accept either an Enrollment or Certificate instance
    certificate = None
    if isinstance(enrollment, Certificate) or hasattr(enrollment, 'certificate_number'):
        certificate = enrollment
        enrollment = certificate.enrollment
        force = True

    if not force:
        eligible, reason = can_generate_certificate(enrollment)
        if not eligible:
            return None, reason

    if not certificate:
        cert_number = f"SJTC{enrollment.id:04d}P{uuid.uuid4().hex[:4].upper()}"
        certificate, created = Certificate.objects.get_or_create(
            enrollment=enrollment,
            defaults={'certificate_number': cert_number}
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.5 * inch,
        leftMargin=2.15 * inch,
        topMargin=0.22 * inch,
        bottomMargin=0.22 * inch,
    )

    story = []
    styles = getSampleStyleSheet()

    # QR Code Generation
    site_url = getattr(settings, 'SITE_URL', 'http://10.243.185.186:8000')
    qr = qrcode.QRCode(version=1, box_size=2, border=1)
    qr.add_data(f"{site_url}/certificate/{certificate.id}/verify/")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0B1B3D", back_color="white")
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_reportlab = Image(qr_buf, width=0.76 * inch, height=0.76 * inch)

    # Signature image
    sig_path = os.path.join(
        settings.BASE_DIR, 'courses', 'static', 'courses', 'images', 'sunny_signature.jpg'
    )
    sig_img = None
    if os.path.exists(sig_path):
        sig_img = Image(sig_path, width=1.6 * inch, height=0.52 * inch)

    # ── Styles (+4pt ALL Boost) ──
    flourish_s = ParagraphStyle(
        'FS', parent=styles['Normal'],
        fontName='Times-Italic', fontSize=18,
        textColor=colors.HexColor('#D97706'),
        alignment=1, spaceAfter=1
    )
    cert_title_s = ParagraphStyle(
        'CT', parent=styles['Heading1'],
        fontName='Times-Bold', fontSize=38,
        textColor=colors.HexColor('#0B1B3D'),
        alignment=1, spaceAfter=1, leading=40
    )
    sub_title_s = ParagraphStyle(
        'ST', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=15.5,
        textColor=colors.HexColor('#D97706'),
        alignment=1, spaceAfter=3
    )
    certify_banner_s = ParagraphStyle(
        'CBS', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14,
        textColor=colors.white,
        alignment=1
    )
    name_s = ParagraphStyle(
        'NS', parent=styles['Heading1'],
        fontName='Times-BoldItalic', fontSize=39,
        textColor=colors.HexColor('#0B1B3D'),
        alignment=1, spaceAfter=1, leading=41
    )
    course_label_s = ParagraphStyle(
        'CLS', parent=styles['Normal'],
        fontName='Helvetica', fontSize=14,
        textColor=colors.HexColor('#475569'),
        alignment=1, spaceAfter=2
    )
    course_name_s = ParagraphStyle(
        'CNS', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=19,
        textColor=colors.HexColor('#0B1B3D'),
        alignment=1, spaceAfter=3, leading=21
    )
    conducted_s = ParagraphStyle(
        'CS', parent=styles['Normal'],
        fontName='Helvetica', fontSize=14,
        textColor=colors.HexColor('#0B1B3D'),
        alignment=1, spaceAfter=1
    )
    desc_s = ParagraphStyle(
        'DS', parent=styles['Normal'],
        fontName='Helvetica', fontSize=12.0,
        textColor=colors.HexColor('#475569'),
        alignment=1, spaceAfter=4, leading=15.0
    )
    meta_label_s = ParagraphStyle(
        'MLS', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10.0,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )
    meta_val_s = ParagraphStyle(
        'MVS', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12.0,
        textColor=colors.HexColor('#0B1B3D'),
        alignment=1
    )
    sign_name_s = ParagraphStyle(
        'SNS', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13.0,
        textColor=colors.HexColor('#0B1B3D'),
        alignment=1
    )
    sign_title_s = ParagraphStyle(
        'STS', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11.0,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )

    # ── Build Story ──
    story.append(Paragraph("---   ~   ---", flourish_s))
    story.append(Spacer(1, 0.04 * inch))
    story.append(Paragraph("CERTIFICATE", cert_title_s))
    story.append(Spacer(1, 0.04 * inch))
    story.append(Paragraph("— OF COMPLETION —", sub_title_s))
    story.append(Spacer(1, 0.12 * inch))

    # Dark Navy Ribbon Banner: THIS IS TO CERTIFY THAT
    cert_banner_table = Table([[Paragraph("THIS IS TO CERTIFY THAT", certify_banner_s)]], colWidths=[3.5 * inch])
    cert_banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0B1B3D')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(cert_banner_table)
    story.append(Spacer(1, 0.12 * inch))

    # Student Name
    student_name = certificate.display_student_name
    if student_name.lower() in ['admin', 'sysadmin', 'sjadmin'] and not certificate.student_name:
        student_name = "Rahul Patil"  # Demo fallback matching reference image if admin account
    story.append(Paragraph(student_name, name_s))
    story.append(Spacer(1, 0.04 * inch))
    story.append(HRFlowable(width="44%", thickness=1.4, color=colors.HexColor('#D97706'), spaceAfter=1))
    story.append(Spacer(1, 0.08 * inch))

    # Course Details
    story.append(Paragraph("has successfully completed the course", course_label_s))
    story.append(Spacer(1, 0.06 * inch))
    course_title_upper = f"—  {certificate.display_course_title.upper()}  —"
    story.append(Paragraph(course_title_upper, course_name_s))
    story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph("conducted by <b>SJ Tech Classes.</b>", conducted_s))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph(
        "We appreciate the dedication, hard work and commitment<br/>shown by the student during the course.",
        desc_s
    ))
    story.append(Spacer(1, 0.12 * inch))

    # ── Course Dates & Duration Meta Section ──
    date_from = enrollment.enrolled_at.strftime("%d %B %Y").upper() if enrollment.enrolled_at else "01 JUNE 2026"
    if certificate.display_issue_date:
        date_to = certificate.display_issue_date.strftime("%d %B %Y").upper()
    elif enrollment.completed_at:
        date_to = enrollment.completed_at.strftime("%d %B %Y").upper()
    else:
        date_to = "30 JULY 2026"
    duration = certificate.display_duration_hours

    meta_table = Table([
        [
            Paragraph("COURSE DURATION", meta_label_s),
            Paragraph("FROM", meta_label_s),
            Paragraph("TO", meta_label_s)
        ],
        [
            Paragraph(f"{duration} HOURS", meta_val_s),
            Paragraph(date_from, meta_val_s),
            Paragraph(date_to, meta_val_s)
        ]
    ], colWidths=[1.7 * inch, 1.8 * inch, 1.8 * inch])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LINEAFTER', (0, 0), (0, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('LINEAFTER', (1, 0), (1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.22 * inch))

    # ── Bottom Section: Circular Stamp | Signature Block | Cert ID & QR Code ──
    stamp_drawing = create_stamp_drawing()

    inst_name = certificate.display_instructor_name.upper()
    inst_title = certificate.display_instructor_title.upper()

    sig_rows = []
    if sig_img:
        sig_rows.append([sig_img])
    else:
        sig_rows.append([Spacer(1, 0.40 * inch)])
    sig_rows.append([HRFlowable(width="85%", thickness=0.8, color=colors.HexColor('#0B1B3D'))])
    sig_rows.append([Paragraph(inst_name, sign_name_s)])
    sig_rows.append([Paragraph(inst_title, sign_title_s)])
    sig_rows.append([Paragraph("SJ TECH CLASSES", sign_title_s)])

    sig_block = Table(sig_rows, colWidths=[2.3 * inch])
    sig_block.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    # Right cert-ID + QR box
    right_box = Table([
        [Paragraph("CERTIFICATE ID", meta_label_s)],
        [Paragraph(certificate.certificate_number, meta_val_s)],
        [Spacer(1, 1)],
        [qr_reportlab],
        [Paragraph("Scan to Verify", ParagraphStyle(
            'tiny', parent=styles['Normal'],
            fontSize=9.5, alignment=1,
            textColor=colors.HexColor('#475569')
        ))],
    ], colWidths=[1.6 * inch])
    right_box.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    # Combine footer: Stamp on Left, Signature in Middle, QR on Right
    footer_table = Table(
        [[stamp_drawing, sig_block, right_box]],
        colWidths=[1.6 * inch, 2.4 * inch, 1.6 * inch]
    )
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(footer_table)

    # Build PDF with onFirstPage=draw_certificate_background so background is drawn BEFORE story!
    doc.build(story, onFirstPage=draw_certificate_background)
    pdf_bytes = buffer.getvalue()

    file_name = f"certificate_{enrollment.id}_{certificate.certificate_number}.pdf"
    if certificate.pdf_file and certificate.pdf_file.name:
        if certificate.pdf_file.storage.exists(certificate.pdf_file.name):
            certificate.pdf_file.storage.delete(certificate.pdf_file.name)

    certificate.pdf_file.save(file_name, ContentFile(pdf_bytes), save=True)

    if notify_student:
        from accounts.emails import send_certificate_ready_email
        send_certificate_ready_email(certificate)

    return certificate, "Certificate generated successfully!"
