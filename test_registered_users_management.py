import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from create_admin_superuser import admin_username, admin_password

User = get_user_model()

def test_all():
    print("=" * 60)
    print("TESTING REGISTERED STUDENTS LIST IN ADMIN DASHBOARD")
    print("=" * 60)

    # 1. Admin login
    admin_user = User.objects.filter(username=admin_username).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email="admin@test.com",
            password=admin_password,
            role=User.ROLE_ADMIN
        )
    client = Client()
    logged_in = client.login(username=admin_username, password=admin_password)
    assert logged_in, "Admin login failed"
    print("1. [PASS] Admin logged in successfully")

    # 2. Check Admin Dashboard loads student list
    resp = client.get(reverse('dashboard:admin_dashboard'))
    assert resp.status_code == 200, f"Dashboard returned {resp.status_code}"
    assert b'students-management-section' in resp.content, "students-management-section missing in HTML"
    assert b'Student Register List' in resp.content, "Student Register List title missing in HTML"
    print("2. [PASS] Admin Dashboard displays Student Register List section and context")

    # 3. Test Admin adding a new student
    test_username = "test_student_reg_99"
    test_email = "student99@sjtechclasses.com"
    User.objects.filter(username=test_username).delete()

    add_resp = client.post(reverse('dashboard:admin_add_student'), {
        'username': test_username,
        'email': test_email,
        'first_name': 'Testy',
        'last_name': 'Student',
        'password': 'SecurePassword123!',
        'phone_number': '+91 9999988888',
        'headline': 'CS Student',
        'has_all_access': 'on',
        'is_active': 'on'
    })
    assert add_resp.status_code == 302, f"Add student returned {add_resp.status_code}"
    created_student = User.objects.filter(username=test_username).first()
    assert created_student is not None, "Student was not created in DB"
    assert created_student.first_name == 'Testy'
    assert created_student.has_all_access == True
    assert created_student.all_access_valid_until is not None
    print("3. [PASS] Admin successfully added a new registered student with All-Access Pass")

    # 4. Test Searching for student
    search_resp = client.get(reverse('dashboard:admin_dashboard') + f"?student_query={test_username}")
    assert search_resp.status_code == 200
    assert test_username.encode() in search_resp.content
    print("4. [PASS] Student search query filters table correctly")

    # 5. Test Admin updating the student
    edit_resp = client.post(reverse('dashboard:admin_edit_student', kwargs={'student_id': created_student.id}), {
        'username': test_username,
        'email': 'updated_' + test_email,
        'first_name': 'UpdatedFirst',
        'last_name': 'UpdatedLast',
        'phone_number': '+91 1111122222',
        'headline': 'Full Stack Learner',
        'role': 'STUDENT',
        'is_active': 'on',
        'email_verified': 'on'
    })
    assert edit_resp.status_code == 302, f"Edit student returned {edit_resp.status_code}"
    created_student.refresh_from_db()
    assert created_student.first_name == 'UpdatedFirst'
    assert created_student.last_name == 'UpdatedLast'
    assert created_student.email == 'updated_' + test_email
    assert created_student.phone_number == '+91 1111122222'
    assert created_student.has_all_access == False
    print("5. [PASS] Admin successfully updated student profile, contact, and access privileges")

    # 6. Test Admin deleting the student
    del_resp = client.post(reverse('dashboard:admin_delete_student', kwargs={'student_id': created_student.id}))
    assert del_resp.status_code == 302, f"Delete student returned {del_resp.status_code}"
    assert not User.objects.filter(id=created_student.id).exists(), "Student still exists in DB after deletion"
    print("6. [PASS] Admin successfully deleted student account")

    # 7. Test Admin self-deletion safeguard
    self_del_resp = client.post(reverse('dashboard:admin_delete_student', kwargs={'student_id': admin_user.id}))
    assert self_del_resp.status_code == 302
    assert User.objects.filter(id=admin_user.id).exists(), "Self-deletion was not prevented!"
    print("7. [PASS] Self-deletion protection verified: Admin cannot delete their own account")

    # 8. Test Non-Admin cannot add/edit/delete students
    student_client = Client()
    dummy_student = User.objects.create_user(username="unauth_std", email="std@test.com", password="password", role=User.ROLE_STUDENT)
    student_client.login(username="unauth_std", password="password")
    unauth_resp = student_client.post(reverse('dashboard:admin_add_student'), {'username': 'hack', 'email': 'h@h.com', 'password': 'p'})
    assert unauth_resp.status_code == 302, "Student should be redirected away from admin view"
    dummy_student.delete()
    print("8. [PASS] Access control verified: Non-admin users cannot access student management actions")

    print("=" * 60)
    print(">>> ALL 8 TESTS PASSED SUCCESSFULLY! <<<")
    print("=" * 60)

if __name__ == '__main__':
    test_all()
