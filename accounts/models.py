from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_STUDENT = 'STUDENT'
    ROLE_INSTRUCTOR = 'INSTRUCTOR'
    ROLE_ADMIN = 'ADMIN'
    
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_INSTRUCTOR, 'Instructor'),
        (ROLE_ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    headline = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. Full Stack Web Developer & Educator")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True, help_text="Instructor UPI ID for earnings payout")
    email_verified = models.BooleanField(default=True)
    logged_in_session_key = models.CharField(max_length=40, blank=True, null=True, help_text="Active session key for single device login enforcement")
    has_all_access = models.BooleanField(default=False, help_text="Designates whether the student has unlocked all courses via All-Access Pass")
    all_access_valid_until = models.DateTimeField(null=True, blank=True, help_text="Expiration date & time for 1-year All-Access Pass")
    is_instructor_approved = models.BooleanField(default=False, help_text="Designates whether this instructor has been approved by an administrator.")

    def is_student(self):
        return self.role == self.ROLE_STUDENT

    def is_instructor(self):
        if self.is_staff or self.is_superuser or self.role == self.ROLE_ADMIN:
            return True
        return self.role == self.ROLE_INSTRUCTOR and self.is_instructor_approved

    def is_pending_instructor(self):
        return self.role == self.ROLE_INSTRUCTOR and not self.is_instructor_approved

    def is_lms_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_all_access_valid(self):
        """Check if student has active, unexpired All-Access Pass."""
        if not self.has_all_access:
            return False
        if not self.all_access_valid_until:
            return True
        from django.utils import timezone
        return self.all_access_valid_until > timezone.now()

    def all_access_days_left(self):
        """Return remaining days of All-Access Pass, 0 if expired, or None if no pass."""
        if not self.has_all_access or not self.all_access_valid_until:
            return None
        from django.utils import timezone
        diff = self.all_access_valid_until - timezone.now()
        return max(0, diff.days)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
