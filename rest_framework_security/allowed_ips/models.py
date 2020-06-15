from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from rest_framework_security.allowed_ips import config

IP_ACTIONS = [
    ('allow', _('Allow IP')),
    ('req_2fa', _('Require multi-factor authentication')),
    ('warn', _('Allow but send email')),
    ('deny', _('Deny IP')),
]


class UserIp(models.Model):
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    action = models.CharField(max_length=12, choices=IP_ACTIONS, blank=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('ip_address', 'user')


class UserIpSettingsBase(models.Model):
    default_ip_action = models.CharField(max_length=12, choices=IP_ACTIONS,
                                         default=config.ALLOW_IPS_DEFAULT_DEFAULT_IP_ACTION)

    class Meta:
        abstract = True
