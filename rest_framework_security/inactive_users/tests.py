from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from rest_framework_security.inactive_users import config


class InactiveUsersTestCase(TestCase):
    @patch("rest_framework_security.emails.EmailMultiAlternatives")
    def test_inactive_user(self, m):
        last_login = timezone.now()
        last_login -= timedelta(
            days=config.INACTIVE_USERS_MIN_DAYS + config.INACTIVE_USERS_REMAINING_DAYS
        )
        user: AbstractUser = get_user_model().objects.create(
            username="demo",
            last_login=last_login,
        )
        call_command("inactive_users")
        self.assertFalse(get_user_model().objects.get(pk=user.pk).is_active)
        m.assert_called_once()


class SendInactiveUserEmailsTestCase(TestCase):
    @patch("rest_framework_security.emails.EmailMultiAlternatives")
    def test_inactive_user(self, m):
        last_login = timezone.now()
        last_login -= timedelta(days=config.INACTIVE_USERS_MIN_DAYS)
        user: AbstractUser = get_user_model().objects.create(
            username="demo",
            last_login=last_login,
        )
        call_command("send_inactive_user_emails")
        m.assert_called_once()
        self.assertTrue(get_user_model().objects.get(pk=user.pk).is_active)
