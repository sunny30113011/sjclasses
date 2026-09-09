import random
import threading
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'SJ TECH CLASSES <sunnywaghmode8@gmail.com>')

def generate_otp():
    return str(random.randint(100000, 999999))


def _send_rich_email(subject, recipient_email, text_content, html_content):
    """
    Utility to dispatch rich HTML emails with plain text fallbacks via Gmail SMTP.
    Dispatched asynchronously in a daemon thread so it never blocks web requests or causes timeouts.
    """
    if not recipient_email:
        return False

    def _worker():
        try:
            msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL, [recipient_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()
    return True


def send_welcome_email(user):
    subject = f"Welcome to SJ TECH CLASSES, {user.first_name or user.username}! 🚀"
    
    text_content = f"""
Hello {user.get_full_name() or user.username},

Welcome to SJ TECH CLASSES (Learn Today, Build Tomorrow)! Your student account is now active.

Username: {user.username}
Email: {user.email}

Start browsing our top-rated courses:
http://127.0.0.1:8000/courses/

Best regards,
SJ TECH CLASSES Team
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
        .btn {{ display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: bold; margin-top: 20px; }}
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
            <p>Hello <strong>{user.get_full_name() or user.username}</strong>,</p>
            <p>Your student account has been successfully created. You now have access to industry-grade courses, interactive quizzes, PDF notes, and certified learning paths.</p>
            
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #4f46e5; margin: 20px 0;">
                <p style="margin: 0;"><strong>Username:</strong> {user.username}</p>
                <p style="margin: 5px 0 0 0;"><strong>Email:</strong> {user.email}</p>
            </div>

            <a href="http://127.0.0.1:8000/courses/" class="btn">Explore Courses Now</a>
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
    subject = f"📲 Payment Submitted (UTR: {payment.utr}) - Pending Admin Verification"
    
    text_content = f"""
Hello {payment.user.get_full_name() or payment.user.username},

We received your manual PhonePe / UPI payment details for '{payment.course.title}'.

- Course: {payment.course.title}
- Amount: ₹{payment.amount}
- UTR Ref Number: {payment.utr}
- Status: Pending Verification

Track payment status on your dashboard:
http://127.0.0.1:8000/dashboard/student/

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
                <tr><td><strong>Course:</strong></td><td>{payment.course.title}</td></tr>
                <tr><td><strong>Amount Paid:</strong></td><td style="color:#2563eb; font-weight:bold;">₹{payment.amount}</td></tr>
                <tr><td><strong>Submitted UTR:</strong></td><td><code>{payment.utr}</code></td></tr>
                <tr><td><strong>Current Status:</strong></td><td><span class="status-badge">Pending Verification</span></td></tr>
            </table>

            <p style="font-size: 13px; color: #64748b;">As soon as admin verifies your UTR & screenshot, your course will automatically unlock!</p>
            <a href="http://127.0.0.1:8000/dashboard/student/" style="display:inline-block; background:#0f172a; color:#fff; text-decoration:none; padding:10px 20px; border-radius:6px; font-weight:bold;">View Student Dashboard</a>
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, payment.user.email, text_content, html_content)
    
    # Notify support/admin email
    send_payment_support_notification(payment)


def send_payment_support_notification(payment):
    support_email = "sunnywaghmode8@gmail.com"
    subject = f"🔔 NEW UPI PAYMENT SUBMITTED - UTR: {payment.utr}"
    
    item_title = payment.course.title if payment.course else "Project Purchase"
    
    text_content = f"""
Hello Admin / Support,

A new manual UPI payment proof has been submitted by a student.

Student Username: {payment.user.username}
Student Email: {payment.user.email}
Course/Item: {item_title}
Amount: ₹{payment.amount}
UTR Reference: {payment.utr}
Submitted On: {payment.paid_on}

Please log in to the SJ TECH CLASSES Admin Panel to verify and approve/reject this payment:
http://127.0.0.1:8000/dashboard/admin-panel/

Best regards,
LMS Automated System
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: #f8fafc; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 2px solid #3b82f6; padding: 30px; }}
        .title {{ color: #1e3a8a; font-size: 20px; font-weight: bold; margin-bottom: 15px; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .table td {{ padding: 10px; border-bottom: 1px solid #f1f5f9; }}
        .btn {{ display: inline-block; background: #3b82f6; color: #ffffff !important; text-decoration: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="title" style="color: #1e3a8a; font-size: 20px; font-weight: bold;">🔔 New Payment Proof Submitted</div>
        <p>A student has uploaded a PhonePe/UPI payment receipt for verification:</p>
        
        <table class="table">
            <tr><td><strong>Student Username:</strong></td><td>{payment.user.username}</td></tr>
            <tr><td><strong>Student Email:</strong></td><td>{payment.user.email}</td></tr>
            <tr><td><strong>Course/Item:</strong></td><td>{item_title}</td></tr>
            <tr><td><strong>Amount:</strong></td><td style="color:#10b981; font-weight:bold;">₹{payment.amount}</td></tr>
            <tr><td><strong>UTR Reference:</strong></td><td><code>{payment.utr}</code></td></tr>
        </table>
        
        <a href="http://127.0.0.1:8000/dashboard/admin-panel/" class="btn">Go to Admin Verification Panel</a>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, support_email, text_content, html_content)


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
    
    # Check if scheduled_at is a string and convert to aware datetime
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

    # Format dates for human reading
    scheduled_time_str = scheduled_at.strftime("%B %d, %Y at %I:%M %p")
    duration_str = f"{live_class.duration_minutes} minutes"
    
    text_content = f"""
Hello,

A live interactive class has been {action_str.lower()} for your enrolled course: '{course.title}'.

- Class Title: {live_class.title}
- Scheduled Time: {scheduled_time_str}
- Duration: {duration_str}
- Meeting Link: {live_class.meeting_link}

We have attached a calendar invite (.ics file) to this email. You can add it to Google Calendar, Outlook, or Apple Calendar to receive reminders.

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
    # Generate ICS calendar content
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
    subject = f"🎉 Course Unlocked! Payment Approved for '{payment.course.title}'"
    
    text_content = f"""
Hello {payment.user.get_full_name() or payment.user.username},

Great news! Your manual UPI payment (UTR: {payment.utr}) of ₹{payment.amount} for '{payment.course.title}' has been APPROVED by admin.

Your course is now 100% unlocked! Start learning right away:
http://127.0.0.1:8000/course/{payment.course.slug}/learn/

SJ TECH CLASSES
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
            <p>Your payment with UTR <code>{payment.utr}</code> has been verified. <strong>{payment.course.title}</strong> is now unlocked and available in your LMS classroom.</p>
            
            <a href="http://127.0.0.1:8000/course/{payment.course.slug}/learn/" class="btn">Start Learning Now 🚀</a>
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, payment.user.email, text_content, html_content)


def send_payment_rejected_email(payment):
    subject = f"❌ Payment Verification Notice - UTR: {payment.utr}"
    
    text_content = f"""
Hello {payment.user.get_full_name() or payment.user.username},

Your submitted payment of ₹{payment.amount} for '{payment.course.title}' could not be verified.

Reason from Admin:
"{payment.admin_note or 'Transaction reference ID or payment screenshot mismatch.'}"

Please check your UTR number and re-submit:
http://127.0.0.1:8000/payment/checkout/{payment.course.id}/

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
            <p>Your payment submission for <strong>{payment.course.title}</strong> (UTR: <code>{payment.utr}</code>) was rejected during admin verification.</p>
            
            <div class="reason-box">
                <strong>Admin Rejection Note:</strong><br>
                {payment.admin_note or 'Transaction reference ID or payment screenshot mismatch.'}
            </div>

            <p style="font-size: 13px; color: #64748b;">If you paid using PhonePe, GPay, or Paytm, please verify the 12-digit UTR and upload a clear screenshot.</p>
            <a href="http://127.0.0.1:8000/payment/checkout/{payment.course.id}/" class="btn">Re-submit Payment Details</a>
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, payment.user.email, text_content, html_content)


def send_course_enrollment_email(enrollment):
    subject = f"Official Course Enrollment: {enrollment.course.title}"
    
    text_content = f"""
Hello {enrollment.student.get_full_name() or enrollment.student.username},

You are officially enrolled in '{enrollment.course.title}'!

Access your classroom:
http://127.0.0.1:8000/course/{enrollment.course.slug}/learn/

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
        <p><a href="http://127.0.0.1:8000/course/{enrollment.course.slug}/learn/" style="display:inline-block; background:#4f46e5; color:#fff; padding:12px 24px; border-radius:6px; text-decoration:none; font-weight:bold;">Go to LMS Classroom</a></p>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, enrollment.student.email, text_content, html_content)


def send_certificate_ready_email(certificate):
    subject = f"🎓 Certificate Issued! {certificate.enrollment.course.title}"
    
    text_content = f"""
Congratulations {certificate.enrollment.student.get_full_name() or certificate.enrollment.student.username}!

Your official SJ TECH CLASSES PDF Certificate ({certificate.certificate_number}) is ready!

Download PDF Certificate:
http://127.0.0.1:8000/certificate/{certificate.enrollment.id}/download/

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
        
        <a href="http://127.0.0.1:8000/certificate/{certificate.enrollment.id}/download/" class="btn">Download PDF Certificate</a>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, certificate.enrollment.student.email, text_content, html_content)


def send_password_reset_otp_email(user, otp_code):
    subject = f"🔑 Password Reset OTP Code: {otp_code} - SJ TECH CLASSES"
    
    text_content = f"""
Hello {user.username},

Your 6-digit Password Reset OTP is: {otp_code}

Enter this code on the password reset page:
http://127.0.0.1:8000/account/verify-otp/

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
    """
    Email notification dispatched when an Admin approves an instructor account.
    """
    subject = "🎉 Congratulations! Your Instructor Account Has Been Approved! | SJ TECH CLASSES"
    name = instructor.get_full_name() or instructor.username

    text_content = f"""
Hello {name},

Great news! Your Instructor application has been reviewed and APPROVED by the Administrator of SJ TECH CLASSES.

You now have full access to:
- Instructor Dashboard & Studio
- Course Builder & Lesson Video Uploads
- Live Class Scheduler (Zoom / Google Meet)
- Student Progress & Performance Analytics

Log in to start building your courses:
http://127.0.0.1:8000/dashboard/instructor/

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
                <a href="http://127.0.0.1:8000/dashboard/instructor/" class="btn">Go to Instructor Studio &rarr;</a>
            </div>
            
            <p style="margin-top: 30px; color: #64748b; font-size: 13px;">If you have any questions or need curriculum assistance, feel free to reach out to our admin team anytime.</p>
        </div>
    </div>
</body>
</html>
"""
    _send_rich_email(subject, instructor.email, text_content, html_content)
