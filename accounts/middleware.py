from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.sessions.models import Session

class SingleDeviceLoginMiddleware:
    """
    Ensures a student can only be logged in on one device at a time.
    If a student logs in on a new device, any request from the previous device
    will immediately be logged out with a clear warning notification.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'is_student') and request.user.is_student():
            current_session_key = request.session.session_key
            stored_session_key = getattr(request.user, 'logged_in_session_key', None)

            # If student has a stored active session and current session does not match it
            if stored_session_key and current_session_key and stored_session_key != current_session_key:
                # Delete the outdated session from the database
                try:
                    Session.objects.filter(session_key=current_session_key).delete()
                except Exception:
                    pass

                # Log out the user from this request
                logout(request)

                messages.warning(
                    request,
                    "⚠️ You have been logged out because your account was logged in from another device. Student accounts are restricted to one device at a time."
                )
                return redirect('accounts:login')

            elif not stored_session_key and current_session_key:
                # First time registration or session key wasn't recorded yet
                request.user.logged_in_session_key = current_session_key
                request.user.save(update_fields=['logged_in_session_key'])

        response = self.get_response(request)
        return response
