from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, RegisteredStudent

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('LMS Profile Information', {'fields': ('role', 'profile_picture', 'bio', 'headline', 'phone_number', 'upi_id', 'has_all_access', 'all_access_valid_until', 'is_instructor_approved', 'email_verified')}),
    )

@admin.register(RegisteredStudent)
class RegisteredStudentAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'has_all_access', 'is_active', 'date_joined')
    list_filter = ('has_all_access', 'is_active', 'email_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('LMS Student Profile & Access', {'fields': ('role', 'profile_picture', 'bio', 'headline', 'phone_number', 'has_all_access', 'all_access_valid_until', 'email_verified')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=User.ROLE_STUDENT)
