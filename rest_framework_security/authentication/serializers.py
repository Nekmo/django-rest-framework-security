import datetime
from logging import getLogger
from typing import Type

from django.apps import apps
from django.contrib.auth import get_user_model, authenticate, logout, login
from django.contrib.sessions.backends.base import SessionBase
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_framework_security.authentication import config
from rest_framework_security.authentication.managers import UserSessionQuerySet
from rest_framework_security.authentication.models import UserSession
from rest_framework_security.authentication.next_steps import get_next_steps, get_next_required_steps
from rest_framework_security.utils import get_client_ip


logger = getLogger('rest_framework_security.authentication')


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'})
    remember_me = serializers.BooleanField(
        write_only=True, required=False, default=False,
    )
    session_expires = serializers.DateTimeField(read_only=True, required=False)
    max_session_renewal = serializers.DateTimeField(read_only=True, required=False)
    next_steps = serializers.ListField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(write_only=True, required=True)
        if config.AUTHENTICATION_USER_SERIALIZER:
            user_serializer_class: Type[serializers.Serializer] = import_string(config.AUTHENTICATION_USER_SERIALIZER)
            self.fields['user'] = user_serializer_class(
                read_only=True, default=None,
            )

    @property
    def username_field(self):
        return get_user_model().USERNAME_FIELD

    def validate(self, data):
        request = self.context['request']
        username = data.get(self.username_field)
        credentials = {
            self.username_field: username,
            'password': data.get('password')
        }
        if apps.is_installed('rest_framework_security.allowed_ips') \
                and get_user_model().objects.filter(username=username).exists():
            from rest_framework_security.allowed_ips.protection import AllowedIpsProtection
            protection = AllowedIpsProtection(
                user=get_user_model().objects.filter(username=username).first(),
                ip=get_client_ip(self.context['request']),
            )
            protection.before_auth()
        user = authenticate(**credentials)
        if user is None and get_user_model().objects.filter(username=username).exists():
            logger.info(f'Authentication error for user {username} from ip {get_client_ip(request)}')
        elif user is None:
            logger.info(f'Attempt to authenticate to non-existent user {username} from ip {get_client_ip(request)}')
        if user is None:
            raise ValidationError('Invalid username or password', 'user_login_failed')
        return {
            'user': user,
            'remember_me': data.get('remember_me'),
        }

    def create(self, validated_data):
        request = self.context['request']
        session: SessionBase = request.session
        now = timezone.now()
        session_age = config.get_session_age(validated_data.get('remember_me'))
        max_age = config.get_max_age(validated_data.get('remember_me'))
        max_session_renewal = now + datetime.timedelta(seconds=max_age)
        ip_address = get_client_ip(request)
        user_agent = request.META['HTTP_USER_AGENT']
        login(request, validated_data['user'])
        session.set_expiry(session_age)
        session['session_updated_at'] = now.isoformat()
        session['max_session_renewal'] = max_session_renewal.isoformat()
        session['remember_me'] = validated_data['remember_me']
        session['ip_address'] = ip_address
        user_sessions: UserSessionQuerySet = UserSession.objects.filter(user=validated_data['user'])
        if not session.session_key:
            session.save()
        user_sessions.expired().clean_and_delete()
        UserSession.objects.get_or_create(
            session_key=session.session_key, user=validated_data['user'],
            defaults={
                'ip_address': ip_address,
                'user_agent': user_agent,
                'session_expires': now + datetime.timedelta(seconds=max_age),
                'max_session_renewal': max_session_renewal,
            }
        )
        user_sessions.apply_max_active_sessions(config.AUTHENTICATION_MAX_ACTIVE_SESSIONS)
        next_steps = list(get_next_required_steps(request))
        logger.info(f'User {validated_data["user"]} authenticated from ip {ip_address}. '
                    f'Next steps: {",".join(next_steps) or "nothing"}')
        return {
            'user': validated_data['user'],
            'session_expires': datetime.datetime.now() + datetime.timedelta(seconds=session_age),
            'max_session_renewal': max_session_renewal,
            'next_steps': next_steps,
        }


class LogoutSerializer(serializers.Serializer):
    def create(self, validated_data):
        request = self.context['request']
        session: SessionBase = request.session
        UserSession.objects.filter(user=request.user, session_key=session.session_key).delete()
        logout(request)
        return {}


class NextStepSerializer(serializers.Serializer):
    step_name = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()


class UserSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSession
        fields = (
            'url', 'id', 'ip_address', 'user_agent', 'browser', 'os', 'device', 'session_expires',
            'max_session_renewal', 'created_at', 'updated_at'
        )
