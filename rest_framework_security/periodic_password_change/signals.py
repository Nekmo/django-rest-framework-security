from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.utils.module_loading import import_string

from rest_framework_security.deny_repeat_password.signals import password_changed
from rest_framework_security.periodic_password_change import config


@receiver(password_changed)
def unset_require_change_password(sender, instance: AbstractUser, **kwargs):
    if not config.PERIODIC_PASSWORD_CHANGE_MODEL:
        return
    model_class = import_string(config.PERIODIC_PASSWORD_CHANGE_MODEL)
    model = model_class.objects.get(user=instance)
    model.require_change_password = False
    model.save()
