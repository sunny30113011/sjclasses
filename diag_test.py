import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.core import mail
from accounts.models import User
from courses.models import Course, Enrollment

# Clean up
User.objects.filter(username__in=['test_instr_alerts', 'test_student_alerts']).delete()
Course.objects.filter(slug='test-course-alerts').delete()

client = Client()

instructor = User.objects.create(
    username='test_instr_alerts',
    email='instr_alerts@example.com',
    role=User.ROLE_INSTRUCTOR
)
instructor.set_password('instr123')
instructor.save()

student = User.objects.create(
    username='test_student_alerts',
    email='student_alerts@example.com',
    role=User.ROLE_STUDENT
)
student.set_password('student123')
student.save()

course = Course.objects.create(
    title='Test Course Alerts',
    instructor=instructor,
    slug='test-course-alerts',
    price=100,
    discount_price=10
)

Enrollment.objects.create(student=student, course=course)

logged_in = client.login(username='test_instr_alerts', password='instr123')
print("Logged in:", logged_in)

schedule_url = reverse('dashboard:schedule_live_class')
post_data = {
    'course_id': course.id,
    'title': 'Test Live Meeting Session',
    'scheduled_at': '2026-09-09 18:00:00+00:00',
    'duration_minutes': 60,
    'meeting_link': 'https://meet.google.com/abc-defg-hij'
}
response = client.post(schedule_url, post_data)
print("Response status:", response.status_code)
print("Response redirect URL:", getattr(response, 'url', None))

# Print messages
from django.contrib.messages import get_messages
messages = list(get_messages(response.wsgi_request))
print("Messages:")
for m in messages:
    print("-", m.message)

# Clean up
course.delete()
student.delete()
instructor.delete()
