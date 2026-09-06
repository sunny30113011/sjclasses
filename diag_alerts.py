import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from django.core import mail
from accounts.models import User
from courses.models import Course, Enrollment, LiveClass

# Clean up
User.objects.filter(username__in=['test_instr_alerts', 'test_student_alerts']).delete()
Course.objects.filter(slug='test-course-alerts').delete()

instructor = User.objects.create(
    username='test_instr_alerts',
    email='instr_alerts@example.com',
    role=User.ROLE_INSTRUCTOR
)
instructor.save()

student = User.objects.create(
    username='test_student_alerts',
    email='student_alerts@example.com',
    role=User.ROLE_STUDENT
)
student.save()

course = Course.objects.create(
    title='Test Course Alerts',
    instructor=instructor,
    slug='test-course-alerts',
    price=100,
    discount_price=10
)

Enrollment.objects.create(student=student, course=course)

live_class = LiveClass.objects.create(
    course=course,
    title='Test Live Meeting Session',
    scheduled_at='2026-09-09 18:00:00+00:00',
    duration_minutes=60,
    meeting_link='https://meet.google.com/abc-defg-hij'
)

from accounts.emails import send_live_class_alert_email
try:
    print("Calling send_live_class_alert_email...")
    res = send_live_class_alert_email(live_class, is_update=False)
    print("Result:", res)
    print("Outbox len:", len(mail.outbox))
    if len(mail.outbox) > 0:
        print("Subject:", mail.outbox[0].subject)
        print("To:", mail.outbox[0].to)
except Exception as e:
    import traceback
    traceback.print_exc()

# Clean up
live_class.delete()
course.delete()
student.delete()
instructor.delete()
