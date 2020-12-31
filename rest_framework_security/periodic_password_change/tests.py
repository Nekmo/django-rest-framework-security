from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase


class NextStepTestCase(TestCase):
    def setUp(self) -> None:
        self.user: AbstractUser = get_user_model().objects.create(
            username='demo', is_superuser=True, is_staff=True,
        )

    def test_admin_url(self):
        url = reverse('admin:index')
        self.client.force_login(self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
