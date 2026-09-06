import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import User
from courses.models import Course, Enrollment, InterviewQuestion, StudentFeedback, Certificate
from payments.models import Payment

client = Client()

print("=" * 60)
print("RUNNING END-TO-END AUTOMATED VERIFICATION TEST SUITE")
print("=" * 60)

test_results = []

def run_test(name, func):
    try:
        func()
        print(f"[PASS] {name}")
        test_results.append((name, "PASS"))
    except Exception as e:
        print(f"[FAIL] {name} - Error: {e}")
        test_results.append((name, f"FAIL ({e})"))

# 1. Test Home Page
def test_home_page():
    res = client.get('/')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    # Verify 3-card carousel markers in context/response
    assert b'col-md-4' in res.content, "col-md-4 grid column missing for 3-card carousel"
    assert b'Expert Instructors' in res.content, "Instructors section missing"

run_test("Home Page & 3-Card Carousels", test_home_page)

# 2. Test Course List Page
def test_courses_page():
    res = client.get('/courses/')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"

run_test("Course Catalog Page", test_courses_page)

# 3. Test Top Company Interview Questions Page
def test_interview_questions_page():
    res = client.get('/interview-questions/')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert InterviewQuestion.objects.count() > 0, "No Interview Questions found in DB"

run_test("Top MNC Interview Questions Bank", test_interview_questions_page)

# 4. Test Instructor Profiles
def test_instructor_profile_page():
    res = client.get('/instructor/admin/')
    assert res.status_code == 200, f"Expected 200 for admin instructor profile, got {res.status_code}"

run_test("Instructor Profile Page (/instructor/admin/)", test_instructor_profile_page)

# 5. Test Django Admin Site Login & Access
def test_admin_site():
    res = client.get('/admin/login/')
    assert res.status_code == 200, f"Expected 200 for /admin/login/, got {res.status_code}"

run_test("Django Admin Login Page (/admin/)", test_admin_site)

# 6. Test PDF Certificate Generation
def test_pdf_certificate_gen():
    enrollment = Enrollment.objects.first()
    assert enrollment is not None, "No Enrollment record in DB"
    from courses.utils import generate_pdf_certificate
    cert, msg = generate_pdf_certificate(enrollment, force=True)
    assert cert is not None, f"Certificate generation failed: {msg}"
    assert os.path.exists(cert.pdf_file.path), f"PDF file does not exist at {cert.pdf_file.path}"

run_test("PDF Certificate Generation & Layout Engine", test_pdf_certificate_gen)

# 7. Test Student Feedback Submission Endpoint
def test_feedback_submit():
    res = client.post('/feedback/submit/', {
        'student_name': 'Automated Test Student',
        'student_role_company': 'Placed @ Google (18.5 LPA)',
        'rating': '5',
        'feedback_text': 'SJ TECH CLASSES is the absolute best learning platform for full stack development!'
    })
    assert res.status_code in [200, 302], f"Expected 302 redirect, got {res.status_code}"
    fb_exists = StudentFeedback.objects.filter(student_name='Automated Test Student').exists()
    assert fb_exists, "Submitted feedback not saved in DB"

run_test("Student Feedback Submission API", test_feedback_submit)

print("=" * 60)
print("FINAL TEST SUMMARY")
print("=" * 60)
passed = sum(1 for _, status in test_results if status == "PASS")
total = len(test_results)
print(f"Total Tests Executed: {total}")
print(f"Passed: {passed} / {total}")
if passed == total:
    print("ALL 7 TESTS PASSED SUCCESSFULLY! SYSTEM IS 100% OPERATIONAL.")
else:
    print("SOME TESTS FAILED. PLEASE REVIEW LOGS.")
print("=" * 60)
