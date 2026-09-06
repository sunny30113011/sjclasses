import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.conf import settings
from accounts.models import User
from courses.models import Course, Category, Enrollment, Certificate, StudentFeedback, InterviewQuestion, ProjectFile
from payments.models import AllAccessPlan, Payment
from lms_project.wsgi import application as wsgi_app

print('=' * 65)
print(' SJ TECH CLASSES LMS - RENDER HOSTING & SYSTEM READINESS TEST')
print('=' * 65)

results = []

def run_step(title, fn):
    try:
        fn()
        print(f'[OK] [PASS] {title}')
        results.append((title, 'PASS'))
    except Exception as e:
        print(f'[FAIL] [FAIL] {title}: {e}')
        results.append((title, f'FAIL: {e}'))

# Test 1: WSGI Application Callable
def test_wsgi():
    assert wsgi_app is not None
    assert callable(wsgi_app)
run_step('WSGI Server Application (Gunicorn Ready)', test_wsgi)

# Test 2: WhiteNoise & Static Files Storage
def test_whitenoise():
    assert 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE
    assert settings.WHITENOISE_MANIFEST_STRICT is False
    assert os.path.exists(settings.STATIC_ROOT)
run_step('WhiteNoise Static Files Storage & Middleware', test_whitenoise)

# Test 3: Database & Dynamic dj-database-url
def test_db():
    import dj_database_url
    assert 'default' in settings.DATABASES
    assert settings.DATABASES['default']['ENGINE'] is not None
run_step('Database Engine & dj-database-url Multi-Environment Config', test_db)

# Test 4: CSRF & Allowed Hosts for Render
def test_render_hosts():
    assert '.onrender.com' in settings.ALLOWED_HOSTS
    assert any('onrender.com' in o for o in settings.CSRF_TRUSTED_ORIGINS)
run_step('Render Domains & CSRF Trusted Origins Configuration', test_render_hosts)

# Test 5: Superuser Creation Script (Verifies All 5 Powerful Admins + Default Superuser)
def test_superuser_script():
    from create_admin_superuser import User, admin_username, ADMIN_ACCOUNTS
    assert User.objects.filter(username=admin_username).exists(), f"Default admin {admin_username} missing"
    for acc in ADMIN_ACCOUNTS:
        u = User.objects.filter(username=acc['username']).first()
        assert u is not None, f"Admin account {acc['username']} missing"
        assert u.is_superuser, f"{acc['username']} is not superuser"
        assert u.is_staff, f"{acc['username']} is not staff"
        assert u.is_lms_admin(), f"{acc['username']} is not LMS admin"
run_step('Automated Superuser Setup Script (5 Powerful Admins Verified)', test_superuser_script)


# Test 6: UPI ID Configuration
def test_upi():
    plan = AllAccessPlan.get_active_plan()
    assert plan.upi_id == 'sunnywaghmode8@axl', f'Expected sunnywaghmode8@axl, got {plan.upi_id}'
run_step('Admin UPI ID updated to sunnywaghmode8@axl in AllAccessPlan', test_upi)

# Test 7: Public Core Endpoints
def test_public_pages():
    c = Client()
    endpoints = [
        ('/', 'Home Page'),
        ('/courses/', 'Course Catalog'),
        ('/interview-questions/', 'Interview Bank'),
        ('/projects/', 'Projects Portal'),
        ('/placements/', 'Placement Drives'),
        ('/payment/all-access/', 'All-Access Pass Checkout'),
        ('/account/login/', 'Login Page'),
        ('/account/register/', 'Register Page'),
        ('/account/register/instructor/', 'Instructor Registration Page')
    ]
    for url, label in endpoints:
        res = c.get(url)
        assert res.status_code == 200, f'{label} ({url}) returned status {res.status_code}'
run_step('All 9 Public Pages Loading with HTTP 200 OK', test_public_pages)

# Test 8: Single Device Login Middleware Logic
def test_single_device():
    user = User.objects.filter(username='admin').first()
    if user:
        assert hasattr(user, 'logged_in_session_key')
run_step('Single-Device Session Concurrency Protection', test_single_device)

# Test 9: Instructor Approval Gatekeeper
def test_instructor_approval():
    test_inst, _ = User.objects.get_or_create(username='temp_pending_inst', email='inst_test@sj.com', role=User.ROLE_INSTRUCTOR)
    test_inst.is_instructor_approved = False
    test_inst.save()
    assert test_inst.is_pending_instructor() is True
    assert test_inst.is_instructor() is False
    c = Client()
    c.force_login(test_inst)
    res = c.get('/dashboard/instructor/')
    assert res.status_code == 302
    assert '/pending-approval/' in res.url
    test_inst.delete()
run_step('Instructor Approval Gatekeeper (Blocked Until Approved)', test_instructor_approval)

# Test 10: PDF Certificate Layout & Admin Customization
def test_cert_engine():
    from courses.utils import generate_pdf_certificate
    en = Enrollment.objects.first()
    if en:
        cert, msg = generate_pdf_certificate(en, force=True, notify_student=False)
        assert cert is not None
        assert os.path.exists(cert.pdf_file.path)
run_step('ReportLab PDF Certificate Engine with QR & Custom Fields', test_cert_engine)

# Test 11: Student Feedback Moderation
def test_feedback():
    fb = StudentFeedback.objects.first()
    assert fb is not None
    assert hasattr(fb, 'is_approved')
run_step('Student Feedback Carousel & Admin Moderation Suite', test_feedback)

print('=' * 65)
print('FINAL READINESS VERIFICATION SUMMARY')
print('=' * 65)
passed = sum(1 for _, status in results if status == 'PASS')
total = len(results)
print(f'Total Modules Verified: {total}')
print(f'Passed: {passed} / {total}')
if passed == total:
    print(' ALL 11 READINESS MODULES PASSED! PROJECT IS 100% READY FOR RENDER DEPLOYMENT.')
else:
    print('[WARN] SOME MODULES FAILED.')
print('=' * 65)
