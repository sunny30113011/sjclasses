from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def instructor_required(view_func):
    """
    Decorator to restrict access to Instructors or Admins only.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not (request.user.is_instructor() or request.user.is_lms_admin()):
            if getattr(request.user, 'is_pending_instructor', lambda: False)():
                messages.warning(request, "Your instructor account is currently pending Admin approval. You will gain full access once approved.")
                return redirect('accounts:instructor_pending_approval')
            messages.error(request, "Access Restricted: Instructor permissions required.")
            return redirect('dashboard:student_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    """
    Decorator to restrict access to Administrators only.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access the Admin Panel.")
            return redirect('accounts:login')
        if not request.user.is_lms_admin():
            messages.error(request, "Access Restricted: Administrator permissions required.")
            return redirect('dashboard:student_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
