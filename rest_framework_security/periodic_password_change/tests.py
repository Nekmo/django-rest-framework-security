from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase


class NextStepTestCase(TestCase):
    def setUp(self) -> None:
        self.user: AbstractUser = get_user_model().objects.create(
            username='demo', is_superuser=True, is_staff=True,
        )

    def test_admin_url(self):
        from rest_framework_security.deny_repeat_password.models import UserPassword
        url = reverse('admin:index')
        self.client.force_login(self.user)
        user_password = UserPassword.objects.create(
            user=self.user, password='salted_secret',
        )
        UserPassword.objects.filter(pk=user_password.pk).update(
            created_at=timezone.now() - timedelta(days=365)
        )
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:password_change'))
