from django.contrib.auth import user_logged_in
from django.contrib.sessions.backends.base import SessionBase
from django.dispatch import receiver
from django.utils import timezone

from rest_framework_security.periodic_password_change.utils import password_is_expired


@receiver(user_logged_in)
def set_periodic_password_change(sender, request, user, **kwargs):
    session: SessionBase = request.session
    if password_is_expired(user):
        session['periodic_password_change'] = True
