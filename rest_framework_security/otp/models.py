from base64 import b32encode
from os import urandom

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField

from rest_framework_security.otp.managers import OTPStaticManager
from rest_framework_security.otp.utils import random_hex, obfuscate

OTP_TYPES = [
    ('hotp', _('HOTP')),
    ('totp', _('TOTP')),
    ('webauthn', _('WebAuthn')),
]
DESTINATION_TYPES = [
    ('sms', _('SMS')),
    ('call', _('Call')),
    ('email', _('Email')),
    ('device', _('Generator device')),
]
OTP_TYPE_ENGINES = {
    'hotp': 'rest_framework_security.otp.engines.hotp.HOTPEngine',
    'totp': 'rest_framework_security.otp.engines.totp.TOTPEngine',
    'webauthn': 'rest_framework_security.otp.engines.webauthn.WebAuthnEngine',
}


def default_key():
    return random_hex(20)


def random_token():
    return b32encode(urandom(5)).decode('utf-8').lower()


def get_engine_class(engine_name):
    return import_string(OTP_TYPE_ENGINES[engine_name])


def get_engine(engine_name):
    return get_engine_class(engine_name)()


class OTPDevice(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='otp_devices')
    title = models.CharField(max_length=80, blank=True)
    otp_type = models.CharField(max_length=24, choices=OTP_TYPES)
    destination_type = models.CharField(max_length=24, choices=DESTINATION_TYPES)
    destination_value = models.CharField(max_length=80, blank=True)
    data = JSONField(blank=True, default=dict)
    # secret_key = models.CharField(max_length=80, default=default_key,
    #                               help_text="A hex-encoded secret key of up to 40 bytes.")
    # digits = models.PositiveSmallIntegerField(choices=[(6, 6), (8, 8)], default=6,
    #                                           help_text="The number of digits to expect in a token.")
    counter = models.BigIntegerField(default=0, help_text="The next counter value to expect.")
    last_use_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_engine(self):
        return get_engine(self.otp_type)

    @property
    def obfuscated_destination_value(self):
        if self.destination_type == 'email':
            username, domain = self.destination_value.split('@', 1)
            domain, ext = domain.split('.', 1)
            return f'{obfuscate(username)}@{obfuscate(domain)}.{ext}'
        return obfuscate(self.destination_value)


class OTPStatic(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='otp_statics')
    token = models.CharField(max_length=16, default=random_token, editable=False)

    objects = OTPStaticManager()
