from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework_security.otp.utils import random_hex, obfuscate

OTP_TYPES = [
    ('hotp', _('HOTP')),
    ('totp', _('TOTP')),
]
DESTINATION_TYPES = [
    ('sms', _('SMS')),
    ('call', _('Call')),
    ('email', _('Email')),
    ('device', _('Generator device')),
]


def default_key():
    return random_hex(20)


class OTPDevice(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='otp_devices')
    title = models.CharField(max_length=80, blank=True)
    otp_type = models.CharField(max_length=24, choices=OTP_TYPES)
    destination_type = models.CharField(max_length=24, choices=DESTINATION_TYPES)
    destination_value = models.CharField(max_length=80, blank=True)
    secret_key = models.CharField(max_length=80, default=default_key,
                                  help_text="A hex-encoded secret key of up to 40 bytes.")
    digits = models.PositiveSmallIntegerField(choices=[(6, 6), (8, 8)], default=6,
                                              help_text="The number of digits to expect in a token.")
    counter = models.BigIntegerField(default=0, help_text="The next counter value to expect.")
    last_use_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def obfuscated_destination_value(self):
        if self.destination_type == 'email':
            username, domain = self.destination_value.split('@', 1)
            domain, ext = domain.split('.', 1)
            return f'{obfuscate(username)}@{obfuscate(domain)}.{ext}'
        return obfuscate(self.destination_value)


class OTPStatic(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='otp_devices')
    token = models.CharField(max_length=16)
