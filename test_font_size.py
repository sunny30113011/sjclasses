import os
import io
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

import pypdfium2
from courses.models import Enrollment
from courses.utils import generate_pdf_certificate

# Test generating certificate for Enrollment #5 or #1
e = Enrollment.objects.first()
print("Using Enrollment:", e)

# We will modify courses/utils.py font sizes directly and test rendering
