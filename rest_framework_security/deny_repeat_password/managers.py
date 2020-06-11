from django.contrib.auth.hashers import check_password
from django.db import models

from rest_framework_security.deny_repeat_password import config


class UserPasswordQuerySet(models.QuerySet):
    def remove_old_passwords(self, user):
        user_passwords = self.filter(user=user)
        max_passwords = config.DENY_REPEAT_PASSWORD_MAX_SAVED_PASSWORDS
        if user_passwords.count() > max_passwords:
            user_passwords = user_passwords.order_by('-created_at')
            first_last = user_passwords[max_passwords]
            to_remove = user_passwords.filter(pk__lte=first_last.pk)
            to_remove.delete()

    def password_exists(self, password):
        last_passwords = self.values_list('password', flat=True)
        for last_password in last_passwords:
            if check_password(password, last_password):
                return True
        return False


class UserPasswordManager(models.Manager):
    def get_queryset(self):
        return UserPasswordQuerySet(self.model, using=self._db)

    def remove_old_passwords(self, user):
        return self.get_queryset().remove_old_passwords(user)

    def password_exists(self, user, password):
        return self.get_queryset().password_exists(password)
