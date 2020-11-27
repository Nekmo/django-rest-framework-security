import datetime

from django.utils import timezone
from django.utils.module_loading import import_string

from rest_framework_security.periodic_password_change import config


def get_last_user_password_change(user):
    from rest_framework_security.deny_repeat_password.models import UserPassword
    user_password: UserPassword = UserPassword.objects.filter(user=user).order_by('-created_at').first()
    if user_password is not None:
        return user_password.created_at


def password_is_expired(user):
    model_class = None
    if config.PERIODIC_PASSWORD_CHANGE_MODEL:
        model_class = import_string(config.PERIODIC_PASSWORD_CHANGE_MODEL)
    if model_class and model_class.objects.get(user=user).require_change_password:
        return True
    last_password_change = get_last_user_password_change(user)
    periodic_change = datetime.timedelta(days=config.PERIODIC_PASSWORD_CHANGE_DAYS)
    return last_password_change and last_password_change + periodic_change < timezone.now()
