import datetime

from django.utils import timezone

from rest_framework_security.periodic_password_change import config


def get_last_user_password_change(user):
    from rest_framework_security.deny_repeat_password.models import UserPassword
    user_password: UserPassword = UserPassword.objects.filter(user=user).order_by('-created_at').first()
    if user_password is not None:
        return user_password.created_at


def password_is_expired(user):
    last_password_change = get_last_user_password_change(user)
    periodic_change = datetime.timedelta(days=config.PERIODIC_PASSWORD_CHANGE_DAYS)
    return last_password_change and last_password_change + periodic_change < timezone.now()
