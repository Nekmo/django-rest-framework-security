import datetime
from functools import wraps

from rest_framework.exceptions import PermissionDenied

from rest_framework_security.sudo import config
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from rest_framework_security.sudo.utils import get_request_argument


def get_user_remaning_time(user: AbstractUser):
    expired_time = datetime.timedelta(seconds=0)
    if not user.last_login:
        return expired_time
    now = timezone.now()
    expiration_time = user.last_login - now + config.REST_FRAMEWORK_SUDO_EXPIRATION
    if expiration_time.total_seconds() < 0:
        return expired_time
    return expiration_time


def expire_now(user: AbstractUser) -> None:
    if not get_user_remaning_time(user):
        return
    user.last_login = timezone.now() - config.REST_FRAMEWORK_SUDO_EXPIRATION - datetime.timedelta(seconds=1)
    user.save()


def get_expires_at(user: AbstractUser):
    return timezone.now() + get_user_remaning_time(user)


def validate_sudo(request):
    if not get_user_remaning_time(request.user):
        raise PermissionDenied('You need to authenticate again to perform this action.')


def sudo_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        request = get_request_argument(args, kwargs)
        if request is None:
            raise AttributeError('request is not available')
        validate_sudo(request)
        return fn(*args, **kwargs)
    return wrapper
