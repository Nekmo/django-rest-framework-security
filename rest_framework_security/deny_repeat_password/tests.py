from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import TestCase

from rest_framework_security.deny_repeat_password import config
from rest_framework_security.deny_repeat_password.models import UserPassword


class DenyRepeatPasswordValidatorTestCase(TestCase):
    def setUp(self) -> None:
        self.user: AbstractUser = get_user_model().objects.create(
            username='demo',
        )
        self.password = 'demo1234'
        self.user.set_password(self.password)
        self.user.save()

    def test_deny_repeat(self):
        with self.assertRaises(ValidationError):
            validate_password(self.password, self.user)
        validate_password('otherpassword1234', self.user)


class UserPasswordQuerySetTestCase(TestCase):
    def setUp(self) -> None:
        self.user: AbstractUser = get_user_model().objects.create(
            username='demo',
        )

    def test_remove_old_passwords(self):
        for i in range(config.DENY_REPEAT_PASSWORD_MAX_SAVED_PASSWORDS + 3):
            self.user.set_password(f'newpassword{i}')
            self.user.save()
        self.assertEqual(UserPassword.objects.count(), config.DENY_REPEAT_PASSWORD_MAX_SAVED_PASSWORDS)
        validate_password('newpassword0', self.user)  # First password is available again
