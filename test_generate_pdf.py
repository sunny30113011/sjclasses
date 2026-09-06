import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from courses.models import Enrollment, Certificate
from courses.utils import generate_pdf_certificate

enrollment = Enrollment.objects.first()
if enrollment:
    # Delete old certificate object to force fresh creation
    Certificate.objects.filter(enrollment=enrollment).delete()
    cert, message = generate_pdf_certificate(enrollment, force=True)
    print("PDF Generation Result:", message)
    if cert and cert.pdf_file:
        print("Fresh Certificate PDF Path:", cert.pdf_file.path)
        print("Fresh Certificate Number:", cert.certificate_number)
