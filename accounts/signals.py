from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def enforce_single_device_login(sender, request, user, **kwargs):
    """
    Ensure student can only be active on one device at a time.
    When a student logs in, update user.logged_in_session_key to the new session.
    """
    if hasattr(user, 'is_student') and user.is_student():
        # Ensure current session has a session_key generated
        if not request.session.session_key:
            request.session.save()

        current_session_key = request.session.session_key
        user.logged_in_session_key = current_session_key
        user.save(update_fields=['logged_in_session_key'])
        logger.info(f"Student {user.username} logged in with session key: {current_session_key}")


@receiver(user_logged_out)
def clear_user_session_on_logout(sender, request, user, **kwargs):
    """
    Clear active session key when student explicitly logs out.
    """
    if user and hasattr(user, 'is_student') and user.is_student():
        if getattr(user, 'logged_in_session_key', None) == request.session.session_key:
            user.logged_in_session_key = None
            user.save(update_fields=['logged_in_session_key'])
