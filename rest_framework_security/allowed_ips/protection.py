from typing import Type, Union, Tuple

from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework.exceptions import PermissionDenied

from rest_framework_security.allowed_ips import config
from rest_framework_security.allowed_ips.emails import WarnNewIpEmail, WarnIpEmail, DenyNewIpEmail
from rest_framework_security.allowed_ips.models import UserIp, UserIpSettingsBase


def get_default_ip_action(user):
    if config.ALLOWED_IPS_USER_IP_CONFIG_MODEL:
        settings_model_class: Type['UserIpSettingsBase'] = import_string(config.ALLOWED_IPS_USER_IP_CONFIG_MODEL)
        settings: Union['UserIpSettingsBase', None] = settings_model_class.objects.filter(user=user).first()
    else:
        settings = None
    return settings.default_ip_action if settings else config.ALLOWED_IPS_DEFAULT_IP_ACTION


class AllowedIpsProtection:
    def __init__(self, user, ip):
        self.user = user
        self.ip = ip

    def get_action(self) -> Tuple[str, bool]:
        """
        :return: (action, is_default)
        """
        ip: Union[UserIp, None] = UserIp.objects.filter(user=self.user, ip_address=self.ip).first()
        action = ip.action if ip else None
        return action or get_default_ip_action(self.user), action is None

    def before_auth(self):
        action, is_default = self.get_action()
        if is_default:
            # It's the first time using this ip address
            user_ip = UserIp.objects.create(
                action='',
                ip_address=self.ip,
                last_used_at=timezone.now(),
                user=self.user
            )
        else:
            user_ip = UserIp.objects.get(
                ip_address=self.ip,
                user=self.user
            )
            user_ip.last_used_at = timezone.now()
            user_ip.save()
        if action == 'deny' and is_default:
            DenyNewIpEmail(self.user, self.ip).send()
        if action == 'deny':
            raise PermissionDenied(detail=f'Your ip {self.ip} is not authorized')
        if action == 'warn' and is_default:
            # Created without content for prevent send again a email
            WarnNewIpEmail(self.user, self.ip).send()
        elif user_ip.action == 'warn':
            WarnIpEmail(self.user, self.ip).send()
