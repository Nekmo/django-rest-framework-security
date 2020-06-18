import datetime

from django.contrib.auth import logout
from django.contrib.sessions.backends.base import SessionBase
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from rest_framework_security.authentication import config
from rest_framework_security.utils import get_client_ip


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        session: SessionBase = request.session
        session_updated_at = parse_datetime(session.get('session_updated_at', ''))
        max_session_renewal = parse_datetime(session.get('max_session_renewal', ''))
        ip_address = session.get('ip_address', '')
        renew_time = datetime.timedelta(seconds=config.AUTHENTICATION_RENEW_TIME)
        now = timezone.now()
        if ip_address and ip_address != get_client_ip(request):
            logout(request)
        elif session_updated_at and max_session_renewal and \
                session_updated_at + renew_time < now and \
                max_session_renewal < now:
            remember_me = session.get('remember_me')
            session.set_expiry(config.get_session_age(remember_me))
            session['session_updated_at'] = now.isoformat()
        response = self.get_response(request)
        return response
