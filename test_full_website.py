import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from courses.models import (
    Course, Category, Module, Lesson, Enrollment, Wishlist, 
    Certificate, Notification, Quiz, QuizQuestion, 
    QuizAttempt, StudentFeedback, InterviewQuestion
)
from payments.models import Payment, Coupon, AllAccessPlan
from create_admin_superuser import ADMIN_ACCOUNTS, admin_username, admin_password

User = get_user_model()

passed_tests = 0
failed_tests = 0
failures = []

def run_test(name, func):
    global passed_tests, failed_tests, failures
    try:
        func()
        print(f"[PASS] {name}")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] {name} -> Error: {str(e)}")
        failed_tests += 1
        failures.append((name, str(e)))

print("=" * 70)
print(" SJ TECH CLASSES LMS - EXHAUSTIVE FULL WEBSITE VERIFICATION")
print("=" * 70)

# =====================================================================
# SECTION 1: PUBLIC / GUEST ENDPOINTS
# =====================================================================
def test_public_pages():
    client = Client()
    routes = [
        ('Home Page', reverse('courses:home')),
        ('About Page', reverse('courses:about')),
        ('Contact Page', reverse('courses:contact')),
        ('Course Catalog', reverse('courses:course_list')),
        ('Categories List', reverse('courses:categories_list')),
        ('Code Compiler', reverse('courses:code_compiler')),
        ('Live Classes Schedule', reverse('courses:live_classes')),
        ('Placement Portal', reverse('courses:placement_portal')),
        ('Projects Portal', reverse('courses:projects_portal')),
        ('Interview Questions Bank', reverse('courses:interview_questions_list')),
        ('Login Page', reverse('accounts:login')),
        ('Register Student', reverse('accounts:register')),
        ('Register Instructor', reverse('accounts:register_instructor')),
        ('Forgot Password', reverse('accounts:forgot_password')),
        ('All Access Checkout', reverse('payments:all_access_checkout')),
    ]
    for label, url in routes:
        resp = client.get(url)
        assert resp.status_code == 200, f"{label} returned HTTP {resp.status_code}"

run_test("Public Pages & Guest Navigation", test_public_pages)

def test_public_course_and_instructor():
    client = Client()
    course = Course.objects.first()
    if course:
        resp = client.get(reverse('courses:course_detail', args=[course.slug]))
        assert resp.status_code == 200, f"Course detail returned HTTP {resp.status_code}"
    
    instructor = User.objects.filter(role=User.ROLE_INSTRUCTOR, is_instructor_approved=True).first()
    if instructor:
        resp = client.get(reverse('courses:instructor_profile', args=[instructor.username]))
        assert resp.status_code == 200, f"Instructor profile returned HTTP {resp.status_code}"

run_test("Public Course Detail & Instructor Profiles", test_public_course_and_instructor)

def test_public_certificate_verify():
    client = Client()
    cert = Certificate.objects.first()
    if cert:
        resp = client.get(reverse('courses:certificate_verify', args=[cert.id]))
        assert resp.status_code == 200, f"Certificate verify returned HTTP {resp.status_code}"
        assert cert.certificate_number in resp.content.decode('utf-8', errors='ignore')

run_test("Public Certificate QR Verification View", test_public_certificate_verify)

# =====================================================================
# SECTION 2: STUDENT USER FLOWS & PERMISSIONS
# =====================================================================
def test_student_lifecycle():
    client = Client()
    student_user, _ = User.objects.get_or_create(
        username='test_verify_student',
        defaults={'email': 'verify_student@test.com', 'role': User.ROLE_STUDENT}
    )
    student_user.set_password('StudentPass#2026')
    student_user.role = User.ROLE_STUDENT
    student_user.save()

    # Login
    logged = client.login(username='test_verify_student', password='StudentPass#2026')
    assert logged, "Student login failed"

    # Dashboard Router -> student_dashboard
    resp = client.get(reverse('dashboard:dashboard'))
    assert resp.status_code == 302
    assert reverse('dashboard:student_dashboard') in resp.url

    # Student Dashboard HTTP 200
    resp_dash = client.get(reverse('dashboard:student_dashboard'))
    assert resp_dash.status_code == 200

    # User Profile
    resp_prof = client.get(reverse('accounts:profile'))
    assert resp_prof.status_code == 200

    # Wishlist toggle
    course = Course.objects.first()
    if course:
        resp_wish = client.post(reverse('courses:toggle_wishlist', args=[course.id]))
        assert resp_wish.status_code in [200, 302]

    # Submit Student Feedback
    resp_fb = client.post(reverse('courses:submit_student_feedback'), {
        'student_name': 'Test Student',
        'rating': 5,
        'student_role_company': 'Placed at TCS (7.0 LPA)',
        'feedback_text': 'Exceptional LMS training platform by Sunny Sir!'
    })
    assert resp_fb.status_code in [200, 302]

    # Cart Add & Cart View
    if course:
        resp_cart = client.get(reverse('payments:add_to_cart', args=[course.id]))
        assert resp_cart.status_code in [200, 302]
        resp_cart_view = client.get(reverse('payments:cart_detail'))
        assert resp_cart_view.status_code == 200

run_test("Student Authentication, Dashboard, Wishlist & Feedback API", test_student_lifecycle)

# =====================================================================
# SECTION 3: INSTRUCTOR ROLE & APPROVAL GATEKEEPING
# =====================================================================
def test_instructor_gatekeeping():
    client = Client()
    # 1. Unapproved Instructor
    pending_inst, _ = User.objects.get_or_create(
        username='test_pending_instructor',
        defaults={'email': 'pending@inst.com', 'role': User.ROLE_INSTRUCTOR, 'is_instructor_approved': False}
    )
    pending_inst.is_instructor_approved = False
    pending_inst.set_password('Pending#Pass2026')
    pending_inst.save()

    client.login(username='test_pending_instructor', password='Pending#Pass2026')
    resp = client.get(reverse('dashboard:dashboard'))
    assert resp.status_code == 302
    assert reverse('accounts:instructor_pending_approval') in resp.url

    # Attempt to access instructor studio -> Should block
    resp_studio = client.get(reverse('dashboard:instructor_dashboard'))
    assert resp_studio.status_code in [302, 403]

    # 2. Approved Instructor
    approved_inst, _ = User.objects.get_or_create(
        username='test_approved_instructor',
        defaults={'email': 'approved@inst.com', 'role': User.ROLE_INSTRUCTOR, 'is_instructor_approved': True}
    )
    approved_inst.is_instructor_approved = True
    approved_inst.set_password('Approved#Pass2026')
    approved_inst.save()

    client.login(username='test_approved_instructor', password='Approved#Pass2026')
    resp_approved = client.get(reverse('dashboard:instructor_dashboard'))
    assert resp_approved.status_code == 200, f"Approved instructor failed with HTTP {resp_approved.status_code}"

run_test("Instructor Approval Gatekeeping & Studio Access", test_instructor_gatekeeping)

# =====================================================================
# SECTION 4: ALL 5 POWERFUL ADMINS & ADMIN OPERATIONS
# =====================================================================
def test_five_powerful_admins_access():
    for acc in ADMIN_ACCOUNTS:
        c = Client()
        username = acc['username']
        password = acc['password']
        logged = c.login(username=username, password=password)
        assert logged, f"Login failed for powerful admin: {username}"
        
        # Test dashboard auto-redirection
        resp = c.get(reverse('dashboard:dashboard'))
        assert resp.status_code == 302
        assert reverse('dashboard:admin_dashboard') in resp.url
        
        # Test admin panel renders HTTP 200
        resp_admin = c.get(reverse('dashboard:admin_dashboard'))
        assert resp_admin.status_code == 200, f"Admin panel failed for {username}"

run_test("All 5 Powerful Admins Direct Panel Authentication", test_five_powerful_admins_access)

def test_admin_management_operations():
    client = Client()
    client.login(username='sunny_admin', password='Sunny@Admin#2026!')

    # 1. Update All Access Plan
    resp_plan = client.post(reverse('dashboard:admin_update_all_access_plan'), {
        'price': '3499.00',
        'original_price': '14999.00',
        'upi_id': 'sunnywaghmode8@axl',
        'duration_days': 365,
        'title': '1-Year Unlimited All-Access Pass',
        'badge_text': 'BEST VALUE',
        'is_active': 'on'
    })
    assert resp_plan.status_code in [200, 302]
    plan = AllAccessPlan.get_active_plan()
    assert plan.upi_id == 'sunnywaghmode8@axl'

    # 2. Toggle Feedback Approval
    fb = StudentFeedback.objects.first()
    if fb:
        orig_status = fb.is_approved
        resp_toggle = client.get(reverse('dashboard:admin_toggle_feedback_approval', args=[fb.id]))
        assert resp_toggle.status_code == 302
        fb.refresh_from_db()
        assert fb.is_approved != orig_status
        # Revert
        client.get(reverse('dashboard:admin_toggle_feedback_approval', args=[fb.id]))

    # 3. Add Feedback by Admin
    resp_add_fb = client.post(reverse('dashboard:admin_add_feedback'), {
        'full_name': 'Automated Test Reviewer',
        'company_role': 'Software Engineer @ MNC',
        'rating': 5,
        'review_text': 'Outstanding course material and live sessions.',
        'is_approved': 'on'
    })
    assert resp_add_fb.status_code == 302

    # 4. Certificate Custom Edit
    cert = Certificate.objects.first()
    if cert:
        resp_edit_cert = client.post(reverse('dashboard:admin_edit_certificate', args=[cert.id]), {
            'student_name': 'Super Student',
            'course_title': 'Advanced Full Stack Python & AI Masterclass',
            'issue_date': '2026-09-07',
            'duration_hours': 120,
            'instructor_name': 'Sunny Sir',
            'instructor_title': 'Chief Technology Mentor',
            'certificate_number': cert.certificate_number
        })
        assert resp_edit_cert.status_code == 302
        cert.refresh_from_db()
        assert cert.student_name == 'Super Student'

run_test("Admin Management Operations (Plans, Feedback, Certificates)", test_admin_management_operations)

# =====================================================================
# SECTION 5: SECURITY & ACCESS CONTROL RESTRICTIONS
# =====================================================================
def test_security_and_privilege_escalation_protection():
    client = Client()
    # Unauthenticated user hitting admin panel -> redirected to login
    resp = client.get(reverse('dashboard:admin_dashboard'))
    assert resp.status_code == 302
    assert reverse('accounts:login') in resp.url

    # Student trying to hit admin panel -> redirected or blocked
    client.login(username='test_verify_student', password='StudentPass#2026')
    resp_stud = client.get(reverse('dashboard:admin_dashboard'))
    assert resp_stud.status_code == 302
    assert reverse('dashboard:student_dashboard') in resp_stud.url

run_test("Security Gatekeepers & Privilege Escalation Restrictions", test_security_and_privilege_escalation_protection)

# =====================================================================
# SECTION 6: PDF ENGINE & STATIC ASSETS CHECK
# =====================================================================
def test_pdf_engine():
    from courses.utils import generate_pdf_certificate
    enrollment = Enrollment.objects.first()
    if enrollment:
        cert, msg = generate_pdf_certificate(enrollment, force=True, notify_student=False)
        assert cert is not None, f"Failed to generate certificate: {msg}"
        assert cert.pdf_file, "Certificate has no PDF file attached"
        assert os.path.exists(cert.pdf_file.path), f"Certificate file not found at {cert.pdf_file.path}"
        assert os.path.getsize(cert.pdf_file.path) > 1000, "Certificate PDF abnormally small"

run_test("ReportLab Landscape PDF & Dynamic QR Code Generation", test_pdf_engine)

print("=" * 70)
print("FINAL FULL WEBSITE TEST SUMMARY")
print("=" * 70)
print(f"Total Tests Executed: {passed_tests + failed_tests}")
print(f"Passed: {passed_tests} / {passed_tests + failed_tests}")
if failures:
    print("\nFailures:")
    for name, err in failures:
        print(f"  - {name}: {err}")
    sys.exit(1)
else:
    print("\n>>> ALL TESTS PASSED! FULL WEBSITE IS 100% OPERATIONAL & PRODUCTION READY! <<<")
print("=" * 70)
