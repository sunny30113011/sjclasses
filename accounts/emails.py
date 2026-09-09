import os
import random
import threading
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)

FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'SJ TECH CLASSES <sunnywaghmode8@gmail.com>')


def get_site_url():
    url = getattr(settings, 'SITE_URL', 'https://sj-tech-classes.onrender.com')
    return url.rstrip('/')


def get_payment_item_title(payment):
    if getattr(payment, 'is_all_access', False):
        return "All-Access VIP Pass (All Courses)"
    elif payment.course:
        return payment.course.title
    else:
        try:
            from courses.models import ProjectPurchase
            purchase = ProjectPurchase.objects.filter(payment=payment).select_related('project').first()
            if purchase and purchase.project:
                return f"Project: {purchase.project.title}"
        except Exception:
            pass
        return "LMS Course / Project Purchase"


def generate_otp():
    return str(random.randint(100000, 999999))


def _send_rich_email(subject, recipient_email, text_content, html_content, attachments=None):
    """
    Utility to dispatch rich HTML emails asynchronously with plain text fallbacks.
    Runs in a background thread so it NEVER blocks user registration, login, or payments.
    """
    if not recipient_email:
        return False

    def _worker():
        try:
            recipients = [recipient_email] if isinstance(recipient_email, str) else list(recipient_email)
            recipients = [r for r in recipients if r]
            if not recipients:
                return

            msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL, recipients)
            msg.attach_alternative(html_content, "text/html")
            if attachments:
                for att in attachments:
                    try:
                        if isinstance(att, tuple):
                            msg.attach(*att)
                        elif isinstance(att, str):
                            msg.attach_file(att)
                    except Exception as e:
                        logger.warning(f"Could not attach file to email: {e}")
            msg.send(fail_silently=False)
        except Exception as e:
            logger.warning(f"Email dispatch warning ({subject}): {e}")

    threading.Thread(target=_worker, daemon=True).start()
    return True


def send_welcome_email(user, raw_password=None):
    """
    Sends welcome email with Username and Password credentials directly to the student or instructor.
    """
    site_url = get_site_url()
    login_url = f"{site_url}/account/login/"
    courses_url = f"{site_url}/courses/"
    name = user.get_full_name() or user.username
    subject = f"Welcome to SJ TECH CLASSES, {user.first_name or user.username}! 🚀 Your Login Credentials"

    password_val = raw_password if raw_password else "(As chosen during registration)"

    text_content = f"""
Hello {name},

Welcome to SJ TECH CLASSES (Learn Today, Build Tomorrow)! Your account is now active.

=======================================================
🔐 YOUR ACCOUNT LOGIN CREDENTIALS:
=======================================================
Username: {user.username}
Password: {password_val}
Email:    {user.email}
=======================================================

Click here to log into your dashboard:
{login_url}

Browse all available courses:
{courses_url}

Best regards,
SJ TECH CLASSES Team
Solapur, Maharashtra • Support: sunnywaghmode8@gmail.com
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 0; }}
        .email-container {{ max-width: 600px; margin: 30px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
        .header {{ background: #0f172a; padding: 30px; text-align: center; color: #ffffff; }}
        .header h1 {{ margin: 0; font-size: 26px; color: #ffffff; }}
        .header p {{ margin: 5px 0 0 0; color: #d97706; font-size: 13px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}
        .content {{ padding: 30px; line-height: 1.6; }}
        .badge {{ background: #eff6ff; color: #2563eb; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 13px; display: inline-block; margin-bottom: 15px; }}
        .cred-box {{ background: #f8fafc; border: 2px solid #3b82f6; border-radius: 10px; padding: 20px; margin: 25px 0; }}
        .cred-title {{ font-size: 16px; font-weight: bold; color: #1e3a8a; margin: 0 0 12px 0; }}
        .cred-row {{ padding: 8px 0; border-bottom: 1px solid #e2e8f0; font-size: 15px; }}
        .cred-label {{ font-weight: bold; color: #475569; width: 110px; display: inline-block; }}
        .cred-code {{ font-family: monospace; background: #e2e8f0; padding: 3px 10px; border-radius: 4px; font-size: 15px; font-weight: bold; color: #0f172a; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: bold; margin-top: 15px; }}
        .footer {{ background: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>SJ TECH CLASSES</h1>
            <p>Learn Today, Build Tomorrow</p>
        </div>
        <div class="content">
            <span class="badge">Registration Successful 🎉</span>
            <h2>Welcome to SJ TECH CLASSES!</h2>
            <p>Hello <strong>{name}</strong>,</p>
            <p>Your account has been successfully created. Here are your personal login credentials. Please keep them safe for future reference:</p>
            
            <div class="cred-box">
                <div class="cred-title">🔐 Your Account Credentials</div>
                <div class="cred-row"><span class="cred-label">Username:</span> <span class="cred-code">{user.username}</span></div>
                <div class="cred-row"><span class="cred-label">Password:</span> <span class="cred-code">{password_val}</span></div>
                <div class="cred-row" style="border-bottom:none;"><span class="cred-label">Email:</span> <span>{user.email}</span></div>
            </div>

            <p style="margin-top: 20px;">You can now log in to access your courses, lecture videos, notes, quizzes, and certificates:</p>
            <div style="text-align: center;">
                <a href="{login_url}" class="btn">Log In to Your Dashboard &rarr;</a>
            </div>
        </div>
        <div class="footer">
            © SJ TECH CLASSES • Solapur, Maharashtra • Support: sunnywaghmode8@gmail.com
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, user.email, text_content, html_content)


def send_otp_email(user, otp_code):
    subject = f"🔐 Your 6-Digit OTP Code: {otp_code} - SJ TECH CLASSES"
    
    text_content = f"""
Hello {user.first_name or user.username},

Your 6-digit Verification OTP Code is: {otp_code}

This code is valid for 10 minutes. Please do not share it with anyone.

SJ TECH CLASSES Security
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; color: #1e293b; padding: 20px; }}
        .card {{ max-width: 500px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; }}
        .otp-box {{ background: #0f172a; color: #fbbf24; font-size: 32px; font-weight: bold; letter-spacing: 8px; padding: 15px; border-radius: 8px; margin: 25px 0; }}
    </style>
</head>
<body>
    <div class="card">
        <h2 style="color: #0f172a; margin-bottom: 5px;">SJ TECH CLASSES</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: 0;">Email Verification & Security</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p>Hello <strong>{user.first_name or user.username}</strong>,</p>
        <p>Use the following 6-digit OTP code to complete your security verification:</p>
        
        <div class="otp-box">{otp_code}</div>
        
        <p style="color: #94a3b8; font-size: 12px;">This OTP is valid for 10 minutes. If you did not request this, please ignore this email.</p>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, user.email, text_content, html_content)


def send_payment_received_email(payment):
    """
    1. Sends payment receipt acknowledgment to the student.
    2. Sends approval request notification email with screenshot to the site admin.
    """
    site_url = get_site_url()
    item_title = get_payment_item_title(payment)
    student_dashboard_url = f"{site_url}/dashboard/student/"
    
    subject = f"📲 Payment Submitted (UTR: {payment.utr}) - Pending Admin Verification"
    
    text_content = f"""
Hello {payment.user.get_full_name() or payment.user.username},

We received your manual PhonePe / UPI payment details for '{item_title}'.

- Item / Course: {item_title}
- Amount Paid: ₹{payment.amount}
- UTR Ref Number: {payment.utr}
- Status: Pending Admin Verification

Track payment status on your student dashboard:
{student_dashboard_url}

Best regards,
SJ TECH CLASSES Billing
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; color: #1e293b; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }}
        .header {{ background: #0f172a; color: #ffffff; padding: 25px; text-align: center; }}
        .content {{ padding: 30px; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .table td {{ padding: 10px; border-bottom: 1px solid #f1f5f9; }}
        .status-badge {{ background: #fef3c7; color: #92400e; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h2 style="margin:0;">SJ TECH CLASSES</h2>
            <p style="margin:5px 0 0 0; color:#d97706; font-size:12px;">Manual UPI Payment Received</p>
        </div>
        <div class="content">
            <p>Hello <strong>{payment.user.get_full_name() or payment.user.username}</strong>,</p>
            <p>Thank you for submitting your payment proof. Your payment details have been logged and sent to our admin team for verification.</p>
            
            <table class="table">
                <tr><td><strong>Item / Course:</strong></td><td>{item_title}</td></tr>
                <tr><td><strong>Amount Paid:</strong></td><td style="color:#2563eb; font-weight:bold;">₹{payment.amount}</td></tr>
                <tr><td><strong>Submitted UTR:</strong></td><td><code>{payment.utr}</code></td></tr>
                <tr><td><strong>Current Status:</strong></td><td><span class="status-badge">Pending Verification</span></td></tr>
            </table>

            <p style="font-size: 13px; color: #64748b;">As soon as admin verifies your UTR & screenshot, your course access will automatically unlock!</p>
            <a href="{student_dashboard_url}" style="display:inline-block; background:#0f172a; color:#fff; text-decoration:none; padding:10px 20px; border-radius:6px; font-weight:bold;">View Student Dashboard</a>
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, payment.user.email, text_content, html_content)
    
    # Notify site's email to review and approve payment!
    send_payment_support_notification(payment)


def send_payment_support_notification(payment):
    """
    Dispatches immediate alert to site administrator email when a student uploads UTR & receipt screenshot.
    """
    site_url = get_site_url()
    item_title = get_payment_item_title(payment)
    admin_panel_url = f"{site_url}/dashboard/admin-panel/"
    django_admin_url = f"{site_url}/admin/payments/payment/{payment.id}/change/"
    
    support_email = getattr(settings, 'SUPPORT_EMAIL', 'sunnywaghmode8@gmail.com')
    site_email = getattr(settings, 'EMAIL_HOST_USER', 'sunnywaghmode8@gmail.com')
    recipients = list({support_email, site_email, 'sunnywaghmode8@gmail.com'})

    subject = f"🚨 [APPROVAL REQUIRED] New UPI Payment ₹{payment.amount} - UTR: {payment.utr} | {payment.user.username}"
    
    paid_time = payment.paid_on.strftime('%B %d, %Y at %I:%M %p') if getattr(payment, 'paid_on', None) else "Just now"
    student_phone = getattr(payment.user, 'phone_number', None) or "Not provided"

    # Screenshot handling
    screenshot_url = ""
    attachments = []
    if payment.screenshot:
        try:
            url = payment.screenshot.url
            if url.startswith('http'):
                screenshot_url = url
            else:
                screenshot_url = f"{site_url}{url}"
        except Exception:
            screenshot_url = ""

        try:
            if hasattr(payment.screenshot, 'path') and os.path.exists(payment.screenshot.path):
                with open(payment.screenshot.path, 'rb') as f:
                    attachments.append((os.path.basename(payment.screenshot.name), f.read(), 'image/jpeg'))
            else:
                payment.screenshot.open('rb')
                attachments.append((os.path.basename(payment.screenshot.name), payment.screenshot.read(), 'image/jpeg'))
        except Exception:
            pass

    text_content = f"""
Hello Admin,

A student has submitted a new manual UPI payment proof that requires your verification and approval.

--------------------------------------------------
PAYMENT DETAILS:
--------------------------------------------------
Student Name:     {payment.user.get_full_name() or payment.user.username}
Student Username: {payment.user.username}
Student Email:    {payment.user.email}
Student Phone:    {student_phone}
Item / Course:    {item_title}
Amount Paid:      ₹{payment.amount}
UTR Ref Number:   {payment.utr}
Submitted On:     {paid_time}
--------------------------------------------------

Screenshot URL:
{screenshot_url or 'Attached to this email'}

To APPROVE or REJECT this payment:
1. Open Admin Verification Panel: {admin_panel_url}
2. Or Direct Django Admin Record: {django_admin_url}

Best regards,
SJ TECH CLASSES Automated System
"""

    screenshot_html_block = ""
    if screenshot_url:
        screenshot_html_block = f"""
        <div style="margin: 20px 0; padding: 15px; background: #f8fafc; border-radius: 8px; border: 1px solid #cbd5e1; text-align: center;">
            <p style="font-weight: bold; margin-top: 0; color: #0f172a;">📸 Uploaded Payment Screenshot Receipt:</p>
            <a href="{screenshot_url}" target="_blank" style="display:inline-block; margin-bottom: 12px; color: #2563eb; font-weight: bold; text-decoration: underline;">
                👉 Click here to Open / Download Full-Size Screenshot
            </a>
            <br>
            <a href="{screenshot_url}" target="_blank">
                <img src="{screenshot_url}" alt="Payment Receipt Screenshot" style="max-width: 100%; max-height: 400px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
            </a>
        </div>
        """

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; padding: 20px; }}
        .card {{ max-width: 620px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 2px solid #ef4444; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #ffffff; padding: 25px; text-align: center; border-bottom: 3px solid #ef4444; }}
        .content {{ padding: 30px; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .table td {{ padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
        .btn-approve {{ display: inline-block; background: #10b981; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; margin-right: 10px; }}
        .btn-admin {{ display: inline-block; background: #3b82f6; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h2 style="margin:0; color:#ffffff;">🔔 PAYMENT APPROVAL REQUIRED</h2>
            <p style="margin:5px 0 0 0; color:#f87171; font-weight:bold; font-size:13px; text-transform:uppercase;">SJ TECH CLASSES Admin Notification</p>
        </div>
        <div class="content">
            <p style="font-size: 15px;">A student has uploaded a PhonePe/UPI payment receipt for admin verification:</p>
            
            <table class="table">
                <tr><td style="width: 140px; color:#64748b;"><strong>Student Name:</strong></td><td><strong>{payment.user.get_full_name() or payment.user.username}</strong></td></tr>
                <tr><td style="color:#64748b;"><strong>Username:</strong></td><td><code>{payment.user.username}</code></td></tr>
                <tr><td style="color:#64748b;"><strong>Email:</strong></td><td><a href="mailto:{payment.user.email}">{payment.user.email}</a></td></tr>
                <tr><td style="color:#64748b;"><strong>Phone:</strong></td><td>{student_phone}</td></tr>
                <tr><td style="color:#64748b;"><strong>Item / Course:</strong></td><td><span style="color:#4f46e5; font-weight:bold;">{item_title}</span></td></tr>
                <tr><td style="color:#64748b;"><strong>Amount Paid:</strong></td><td><span style="color:#10b981; font-size:18px; font-weight:bold;">₹{payment.amount}</span></td></tr>
                <tr><td style="color:#64748b;"><strong>UTR Reference:</strong></td><td><code style="background:#fef3c7; padding:4px 8px; border-radius:4px; font-size:15px; color:#92400e; font-weight:bold;">{payment.utr}</code></td></tr>
                <tr><td style="color:#64748b;"><strong>Submitted On:</strong></td><td>{paid_time}</td></tr>
            </table>
            
            {screenshot_html_block}

            <div style="text-align: center; margin-top: 25px;">
                <a href="{admin_panel_url}" class="btn-approve">👉 Verify in Admin Panel</a>
                <a href="{django_admin_url}" class="btn-admin">Django Admin Detail</a>
            </div>
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, recipients, text_content, html_content, attachments=attachments)


def send_live_class_alert_email(live_class, is_update=False):
    from datetime import datetime, timezone as dt_timezone, timedelta
    from django.utils import timezone
    from django.utils.dateparse import parse_datetime
    from courses.models import Enrollment
    
    course = live_class.course
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    recipient_emails = [en.student.email for en in enrollments if en.student.email]
    
    if not recipient_emails:
        return
        
    action_str = "Rescheduled" if is_update else "Scheduled"
    subject = f"📢 Live Class {action_str}: {live_class.title} - {course.title}"
    
    scheduled_at = live_class.scheduled_at
    if isinstance(scheduled_at, str):
        parsed = parse_datetime(scheduled_at)
        if parsed:
            if timezone.is_naive(parsed):
                scheduled_at = timezone.make_aware(parsed)
            else:
                scheduled_at = parsed
        else:
            try:
                from dateutil.parser import parse
                scheduled_at = parse(live_class.scheduled_at)
            except Exception:
                scheduled_at = datetime.now()

    scheduled_time_str = scheduled_at.strftime("%B %d, %Y at %I:%M %p")
    duration_str = f"{live_class.duration_minutes} minutes"
    
    text_content = f"""
Hello,

A live interactive class has been {action_str.lower()} for your enrolled course: '{course.title}'.

- Class Title: {live_class.title}
- Scheduled Time: {scheduled_time_str}
- Duration: {duration_str}
- Meeting Link: {live_class.meeting_link}

We have attached a calendar invite (.ics file) to this email.

See you in class!
Best regards,
SJ TECH CLASSES Team
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }}
        .header {{ background: #0f172a; color: #ffffff; padding: 25px; text-align: center; }}
        .content {{ padding: 30px; line-height: 1.6; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .table td {{ padding: 10px; border-bottom: 1px solid #f1f5f9; }}
        .btn {{ display: inline-block; background: #d97706; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h2 style="margin:0; color:#ffffff;">SJ TECH CLASSES</h2>
            <p style="margin:5px 0 0 0; color:#fbbf24; font-size:12px; font-weight:bold; text-transform:uppercase;">Live Class Scheduled</p>
        </div>
        <div class="content">
            <p>Hello Student,</p>
            <p>A live interactive class session has been <strong>{action_str.lower()}</strong> for your course <strong>{course.title}</strong>.</p>
            
            <table class="table">
                <tr><td><strong>Session Title:</strong></td><td>{live_class.title}</td></tr>
                <tr><td><strong>Scheduled Time:</strong></td><td style="color:#2563eb; font-weight:bold;">{scheduled_time_str}</td></tr>
                <tr><td><strong>Duration:</strong></td><td>{duration_str}</td></tr>
                <tr><td><strong>Meeting Link:</strong></td><td><a href="{live_class.meeting_link}" target="_blank">{live_class.meeting_link}</a></td></tr>
            </table>

            <p style="font-size: 13px; color: #64748b;">Please open the attached calendar invite (.ics file) to save this event to your calendar.</p>
            <a href="{live_class.meeting_link}" class="btn">Join Class Session</a>
        </div>
    </div>
</body>
</html>
"""
    try:
        dt_start_utc = scheduled_at.astimezone(dt_timezone.utc)
        dt_end_utc = dt_start_utc + timedelta(minutes=int(live_class.duration_minutes))
        
        dtstart_str = dt_start_utc.strftime('%Y%m%dT%H%M%SZ')
        dtend_str = dt_end_utc.strftime('%Y%m%dT%H%M%SZ')
        dtstamp_str = datetime.now(dt_timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SJ TECH CLASSES//LMS//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:live-class-{live_class.id}@sjtechclasses.com
DTSTAMP:{dtstamp_str}
DTSTART:{dtstart_str}
DTEND:{dtend_str}
SUMMARY:{live_class.title} - {course.title}
DESCRIPTION:Join live class: {live_class.meeting_link}
LOCATION:{live_class.meeting_link}
END:VEVENT
END:VCALENDAR"""

    except Exception:
        ics_content = ""

    def _worker():
        try:
            from django.core.mail import EmailMultiAlternatives
            msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL, recipient_emails)
            msg.attach_alternative(html_content, "text/html")
            if ics_content:
                msg.attach(f"invite_{live_class.id}.ics", ics_content, "text/calendar")
            msg.send(fail_silently=True)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()
    return True


def send_payment_approved_email(payment):
    site_url = get_site_url()
    item_title = get_payment_item_title(payment)
    if getattr(payment, 'is_all_access', False):
        learn_url = f"{site_url}/courses/"
    elif payment.course:
        learn_url = f"{site_url}/course/{payment.course.slug}/learn/"
    else:
        learn_url = f"{site_url}/dashboard/student/"

    subject = f"🎉 Access Unlocked! Payment Approved for '{item_title}'"
    
    text_content = f"""
Hello {payment.user.get_full_name() or payment.user.username},

Great news! Your manual UPI payment (UTR: {payment.utr}) of ₹{payment.amount} for '{item_title}' has been APPROVED by admin.

Your access is now 100% unlocked! Start learning right away:
{learn_url}

Best regards,
SJ TECH CLASSES Team
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; color: #1e293b; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; text-align: center; }}
        .header {{ background: #065f46; color: #ffffff; padding: 30px; }}
        .content {{ padding: 30px; }}
        .btn {{ display: inline-block; background: #059669; color: #ffffff !important; text-decoration: none; padding: 14px 30px; border-radius: 8px; font-weight: bold; font-size: 16px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h1 style="margin:0; font-size:28px;">🎉 PAYMENT APPROVED!</h1>
            <p style="margin:5px 0 0 0; opacity:0.9;">Course Access Granted</p>
        </div>
        <div class="content">
            <p>Hello <strong>{payment.user.get_full_name() or payment.user.username}</strong>,</p>
            <p>Your payment with UTR <code>{payment.utr}</code> has been verified. <strong>{item_title}</strong> is now unlocked and available in your LMS classroom.</p>
            
            <a href="{learn_url}" class="btn">Start Learning Now 🚀</a>
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, payment.user.email, text_content, html_content)


def send_payment_rejected_email(payment):
    site_url = get_site_url()
    item_title = get_payment_item_title(payment)
    if getattr(payment, 'is_all_access', False):
        retry_url = f"{site_url}/payment/all-access/"
    elif payment.course:
        retry_url = f"{site_url}/payment/checkout/{payment.course.id}/"
    else:
        retry_url = f"{site_url}/projects/"

    subject = f"❌ Payment Verification Notice - UTR: {payment.utr}"
    
    text_content = f"""
Hello {payment.user.get_full_name() or payment.user.username},

Your submitted payment of ₹{payment.amount} for '{item_title}' could not be verified.

Reason from Admin:
"{payment.admin_note or 'Transaction reference ID or payment screenshot mismatch.'}"

Please check your UTR number and re-submit:
{retry_url}

SJ TECH CLASSES Billing
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; color: #1e293b; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }}
        .header {{ background: #991b1b; color: #ffffff; padding: 25px; text-align: center; }}
        .content {{ padding: 30px; }}
        .reason-box {{ background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; color: #991b1b; margin: 20px 0; border-radius: 4px; }}
        .btn {{ display: inline-block; background: #dc2626; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h2 style="margin:0;">Payment Verification Update</h2>
        </div>
        <div class="content">
            <p>Hello <strong>{payment.user.get_full_name() or payment.user.username}</strong>,</p>
            <p>Your payment submission for <strong>{item_title}</strong> (UTR: <code>{payment.utr}</code>) was rejected during admin verification.</p>
            
            <div class="reason-box">
                <strong>Admin Rejection Note:</strong><br>
                {payment.admin_note or 'Transaction reference ID or payment screenshot mismatch.'}
            </div>

            <p style="font-size: 13px; color: #64748b;">If you paid using PhonePe, GPay, or Paytm, please verify the 12-digit UTR and upload a clear screenshot.</p>
            <a href="{retry_url}" class="btn">Re-submit Payment Details</a>
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, payment.user.email, text_content, html_content)


def send_course_enrollment_email(enrollment):
    site_url = get_site_url()
    course_url = f"{site_url}/course/{enrollment.course.slug}/learn/"
    subject = f"Official Course Enrollment: {enrollment.course.title}"
    
    text_content = f"""
Hello {enrollment.student.get_full_name() or enrollment.student.username},

You are officially enrolled in '{enrollment.course.title}'!

Access your classroom:
{course_url}

SJ TECH CLASSES
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0; }}
    </style>
</head>
<body>
    <div class="card">
        <h2 style="color: #0f172a; margin-top:0;">SJ TECH CLASSES</h2>
        <h3>Course Enrollment Confirmed! 🎓</h3>
        <p>Hello <strong>{enrollment.student.get_full_name() or enrollment.student.username}</strong>,</p>
        <p>You have been enrolled in <strong>{enrollment.course.title}</strong>.</p>
        <p><a href="{course_url}" style="display:inline-block; background:#4f46e5; color:#fff; padding:12px 24px; border-radius:6px; text-decoration:none; font-weight:bold;">Go to LMS Classroom</a></p>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, enrollment.student.email, text_content, html_content)


def send_certificate_ready_email(certificate):
    site_url = get_site_url()
    download_url = f"{site_url}/certificate/{certificate.enrollment.id}/download/"
    subject = f"🎓 Certificate Issued! {certificate.enrollment.course.title}"
    
    text_content = f"""
Congratulations {certificate.enrollment.student.get_full_name() or certificate.enrollment.student.username}!

Your official SJ TECH CLASSES PDF Certificate ({certificate.certificate_number}) is ready!

Download PDF Certificate:
{download_url}

SJ TECH CLASSES (Learn Today, Build Tomorrow)
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 2px solid #d97706; padding: 35px; text-align: center; }}
        .title {{ color: #0f172a; font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
        .badge {{ background: #fef3c7; color: #b45309; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 14px; display: inline-block; margin-bottom: 15px; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); color: #ffffff !important; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: bold; font-size: 16px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">Official SJ TECH Certificate Issued</span>
        <div class="title">CONGRATULATIONS! 🎓</div>
        <p>Hello <strong>{certificate.enrollment.student.get_full_name() or certificate.enrollment.student.username}</strong>,</p>
        <p>You have successfully completed 100% of the lessons and passed all quizzes for <strong>{certificate.enrollment.course.title}</strong>!</p>
        
        <p style="font-size:14px; color:#64748b;">Certificate ID: <code>{certificate.certificate_number}</code></p>
        
        <a href="{download_url}" class="btn">Download PDF Certificate</a>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, certificate.enrollment.student.email, text_content, html_content)


def send_password_reset_otp_email(user, otp_code):
    site_url = get_site_url()
    verify_url = f"{site_url}/account/verify-otp/"
    subject = f"🔑 Password Reset OTP Code: {otp_code} - SJ TECH CLASSES"
    
    text_content = f"""
Hello {user.username},

Your 6-digit Password Reset OTP is: {otp_code}

Enter this code on the password reset page:
{verify_url}

SJ TECH Security
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; padding: 20px; }}
        .card {{ max-width: 500px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; }}
        .otp-box {{ background: #0f172a; color: #38bdf8; font-size: 32px; font-weight: bold; letter-spacing: 8px; padding: 15px; border-radius: 8px; margin: 25px 0; }}
    </style>
</head>
<body>
    <div class="card">
        <h2 style="color: #0f172a; margin-top:0;">SJ TECH CLASSES</h2>
        <p style="color: #64748b; font-size: 14px;">Password Reset Request</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p>Hello <strong>{user.username}</strong>,</p>
        <p>Use the following 6-digit OTP code to reset your account password:</p>
        
        <div class="otp-box">{otp_code}</div>
        
        <p style="color: #94a3b8; font-size: 12px;">If you did not request a password reset, please ignore this message.</p>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, user.email, text_content, html_content)


def send_instructor_approved_email(instructor):
    site_url = get_site_url()
    instructor_dashboard_url = f"{site_url}/dashboard/instructor/"
    name = instructor.get_full_name() or instructor.username
    subject = "🎉 Congratulations! Your Instructor Account Has Been Approved! | SJ TECH CLASSES"

    text_content = f"""
Hello {name},

Great news! Your Instructor application has been reviewed and APPROVED by the Administrator of SJ TECH CLASSES.

You now have full access to:
- Instructor Dashboard & Studio
- Course Builder & Lesson Video Uploads
- Live Class Scheduler (Zoom / Google Meet)
- Student Progress & Performance Analytics

Log in to start building your courses:
{instructor_dashboard_url}

Happy Teaching!
SJ TECH CLASSES Team
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 0; }}
        .card {{ max-width: 580px; margin: 30px auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px rgba(0,0,0,0.08); }}
        .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center; color: #ffffff; }}
        .content {{ padding: 30px; line-height: 1.6; }}
        .btn {{ display: inline-block; background: #0f172a; color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: bold; margin-top: 20px; }}
        .feature-box {{ background: #f0fdf4; border-left: 4px solid #10b981; padding: 15px; border-radius: 6px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h1 style="margin:0; font-size: 24px;">🎉 Instructor Account Approved!</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Welcome to the SJ TECH Teaching Community</p>
        </div>
        <div class="content">
            <p>Hello <strong>{name}</strong>,</p>
            <p>We are thrilled to inform you that your application to teach on <strong>SJ TECH CLASSES</strong> has been <strong>approved by the Admin</strong>!</p>
            
            <div class="feature-box">
                <strong style="color: #065f46;">Your Teaching Privileges Are Now Active:</strong>
                <ul style="margin: 8px 0 0 0; padding-left: 20px; color: #047857; font-size: 14px;">
                    <li>Access the dedicated <strong>Instructor Studio</strong></li>
                    <li>Create video courses and structured curriculum modules</li>
                    <li>Host live Zoom / Meet classes with students</li>
                    <li>Receive automated earnings payouts to UPI: <code>{instructor.upi_id or 'Set in Profile'}</code></li>
                </ul>
            </div>

            <div style="text-align: center;">
                <a href="{instructor_dashboard_url}" class="btn">Go to Instructor Studio &rarr;</a>
            </div>
            
            <p style="margin-top: 30px; color: #64748b; font-size: 13px;">If you have any questions or need curriculum assistance, feel free to reach out to our admin team anytime.</p>
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, instructor.email, text_content, html_content)
