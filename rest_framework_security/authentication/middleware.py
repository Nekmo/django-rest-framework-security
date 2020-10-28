import datetime
from typing import Union

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.base import SessionBase
from django.urls import reverse, NoReverseMatch, ResolverMatch, resolve, Resolver404
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from rest_framework_security.authentication import config
from rest_framework_security.authentication.models import UserSession
from rest_framework_security.authentication.next_steps import get_next_steps
from rest_framework_security.utils.ip import get_client_ip


DEFAULT_ALLOWED_URLS = [
    'authentication-next_steps',
    'authentication-login',
    'authentication-logout',
]


def get_admin_base_url(name='index'):
    try:
        return reverse(f'admin:{name}')
    except NoReverseMatch:
        return


def is_path_allowed(path, allowed_urls):
    allowed_urls = list(allowed_urls or [])
    allowed_urls.extend(config.AUTHENTICATION_NEXT_STEPS_AUTHORIZED_URLS)
    try:
        match: ResolverMatch = resolve(path)
    except Resolver404:
        return False
    return path in allowed_urls or match.url_name in allowed_urls


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        session: SessionBase = request.session
        self.validate_and_renew_session(request, session)
        redirect = self.next_steps(request)
        if redirect:
            return redirect
        response = self.get_response(request)
        return response

    def next_steps(self, request):
        admin_base_url = get_admin_base_url('index')
        next_step_required = False
        allowed_urls = list(DEFAULT_ALLOWED_URLS)
        admin_redirect = None
        for next_step in get_next_steps():
            is_required = None
            if request.user.is_authenticated and next_step.is_active(request) is not False:
                is_required = next_step.is_required(request)
                next_step.set_state(request, is_required)
                next_step_required = next_step_required or is_required
            if is_required:
                allowed_urls.extend(next_step.get_allowed_urls())
                admin_redirect = admin_redirect or next_step.get_admin_redirect()
        if next_step_required and is_path_allowed(request.path, allowed_urls):
            pass
        elif next_step_required and admin_redirect and \
                ((admin_base_url and request.path.startswith(admin_base_url)) or
                 (request.path == getattr(settings, 'LOGIN_REDIRECT_URL', '/accounts/profile/'))):
            return admin_redirect
        elif next_step_required:
            request.user = AnonymousUser()

    def validate_and_renew_session(self, request, session):
        session_updated_at = parse_datetime(session.get('session_updated_at', ''))
        max_session_renewal = parse_datetime(session.get('max_session_renewal', ''))
        ip_address = session.get('ip_address', '')
        renew_time = datetime.timedelta(seconds=config.AUTHENTICATION_RENEW_TIME)
        now = timezone.now()
        if ip_address and ip_address != get_client_ip(request):
            logout(request)
        elif not request.user.is_authenticated:
            return 
        elif session_updated_at and max_session_renewal and \
                session_updated_at + renew_time < now <= max_session_renewal:
            remember_me = session.get('remember_me')
            session.set_expiry(config.get_session_age(remember_me))
            session['session_updated_at'] = now.isoformat()
            user_session: Union[UserSession, None] = UserSession.objects.filter(
                user=request.user,
                session_key=session.session_key
            ).first()
            if user_session:
                session_expires = now + datetime.timedelta(
                    seconds=config.get_session_age(remember_me)
                )
                user_session.session_expires = session_expires
                user_session.save()
