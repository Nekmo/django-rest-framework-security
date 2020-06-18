import datetime
from typing import Type

from django.contrib.auth import get_user_model, authenticate
from django.contrib.sessions.backends.base import SessionBase
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_framework_security.authentication import config


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
        credentials = {
            self.username_field: data.get(self.username_field),
            'password': data.get('password')
        }
        user = authenticate(**credentials)
        if user is None:
            raise ValidationError('Invalid username or password', 'user_login_failed')
        return {
            'user': user,
            'remember_me': data.get('remember_me'),
        }

    def create(self, validated_data):
        session: SessionBase = self.context['request'].session
        session_age = config.AUTHENTICATION_REMEMBER_ME_SESSION_AGE if validated_data.get('remember_me') \
            else config.AUTHENTICATION_SESSION_AGE
        max_age = config.AUTHENTICATION_REMEMBER_ME_MAX_AGE if validated_data.get('remember_me') \
            else config.AUTHENTICATION_MAX_AGE
        session.set_expiry(session_age)
        session.cycle_key()
        return {
            'user': validated_data['user'],
            'session_expires': datetime.datetime.now() + datetime.timedelta(seconds=session_age),
            'max_session_renewal': datetime.datetime.now() + datetime.timedelta(seconds=max_age),
            'next_steps': [],
        }
