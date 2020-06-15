from typing import Type, Union, Tuple

from django.utils.module_loading import import_string

from rest_framework_security.allowed_ips import config
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
        return action or get_default_ip_action(self.user), not bool(action)
