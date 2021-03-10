from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework_security.authentication.next_steps import get_admin_base_url


class NextStepTestCase(TestCase):
    def setUp(self) -> None:
        from rest_framework_security.deny_repeat_password.models import UserPassword

        self.user: AbstractUser = get_user_model().objects.create(
            username="demo",
            is_superuser=True,
            is_staff=True,
        )
        self.user_password = UserPassword.objects.create(
            user=self.user,
            password="salted_secret",
        )
        UserPassword.objects.filter(pk=self.user_password.pk).update(
            created_at=timezone.now() - timedelta(days=365)
        )

    def test_admin_url(self):
        url = reverse("admin:index")
        self.client.force_login(self.user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("admin:password_change"))

    def test_allowed_url(self):
        url = get_admin_base_url("password_change")
        self.client.force_login(self.user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_anonymous_url(self):
        url = reverse("usersession-list")
        self.client.force_login(self.user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)

    def test_next_steps(self):
        url = reverse("authentication-next_steps")
        self.client.force_login(self.user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_password_updated(self):
        url = reverse("usersession-list")
        self.client.force_login(self.user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.user_password.save()  # updated created_at
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
