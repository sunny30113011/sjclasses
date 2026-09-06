import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from django.test import Client
from accounts.models import User
from courses.models import Enrollment

client = Client()
users = User.objects.all()

print("=" * 60)
print("TESTING /certificate/1/download/ FOR ALL USERS")
print("=" * 60)

for u in users:
    client.force_login(u)
    res = client.get('/certificate/1/download/')
    print(f"User: {u.username:<12} Role: {u.role:<12} Status: {res.status_code} Size: {len(res.content)} bytes")

print("=" * 60)
