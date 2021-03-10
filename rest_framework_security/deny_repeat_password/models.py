from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework_security.deny_repeat_password.managers import UserPasswordManager


class UserPassword(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    password = models.CharField(_("password"), max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserPasswordManager()
