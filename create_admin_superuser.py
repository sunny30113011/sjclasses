import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'sunnywaghmode8@gmail.com')
admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin1234')

# 5 Dedicated Powerful Admin Credentials for Production LMS Administration
ADMIN_ACCOUNTS = [
    {
        'username': 'sunny_admin',
        'email': 'sunnywaghmode8@gmail.com',
        'password': os.environ.get('ADMIN_PASSWORD_SUNNY', 'Sunny@Admin#2026!'),
        'first_name': 'Sunny',
        'last_name': 'Waghmode',
        'designation': 'Founder & Executive Administrator',
    },
    {
        'username': 'superadmin',
        'email': 'superadmin@sjtechclasses.com',
        'password': os.environ.get('ADMIN_PASSWORD_SUPER', 'SJTech#MasterAdmin99'),
        'first_name': 'SJ Tech',
        'last_name': 'SuperAdmin',
        'designation': 'Master System Administrator',
    },
    {
        'username': 'director_admin',
        'email': 'director@sjtechclasses.com',
        'password': os.environ.get('ADMIN_PASSWORD_DIRECTOR', 'Director@SJTech2026$'),
        'first_name': 'Academic',
        'last_name': 'Director',
        'designation': 'Academic & Curriculum Director',
    },
    {
        'username': 'operations_admin',
        'email': 'operations@sjtechclasses.com',
        'password': os.environ.get('ADMIN_PASSWORD_OPS', 'OpsSJ#Control2026!'),
        'first_name': 'Operations',
        'last_name': 'Head',
        'designation': 'Finance & Payment Verification Officer',
    },
    {
        'username': 'techlead_admin',
        'email': 'techlead@sjtechclasses.com',
        'password': os.environ.get('ADMIN_PASSWORD_TECH', 'TechLead#Secure2026*'),
        'first_name': 'Technical',
        'last_name': 'Lead',
        'designation': 'Cloud Security & Engineering Lead',
    },
]

def setup_admin_user(username, email, password, first_name='', last_name=''):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.role = User.ROLE_ADMIN
    user.is_instructor_approved = True
    user.is_active = True
    user.save()
    status_label = 'CREATED' if created else 'VERIFIED/UPDATED'
    print(f'==> [{status_label}] Admin: {username} | Email: {email}')
    return user

# 1. Ensure the default admin exists for backward compatibility and testing
setup_admin_user(
    username=admin_username,
    email=admin_email,
    password=admin_password,
    first_name='Sunny',
    last_name='Sir'
)

# 2. Ensure all 5 powerful production administrator accounts exist with full superuser permissions
print('==> Provisioning 5 Powerful Production Admin Accounts...')
for acc in ADMIN_ACCOUNTS:
    setup_admin_user(
        username=acc['username'],
        email=acc['email'],
        password=acc['password'],
        first_name=acc['first_name'],
        last_name=acc['last_name']
    )

print('==> All 5 Powerful Administrators + Default Superuser are Active and Ready!')

