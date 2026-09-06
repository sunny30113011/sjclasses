import os
import io
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

import pypdfium2
from courses.models import Enrollment
from courses.utils import generate_pdf_certificate

e = Enrollment.objects.first()
print("First Enrollment:", e)
