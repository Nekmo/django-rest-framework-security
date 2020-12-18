from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class LoginAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('authentication-login')
        self.user: AbstractUser = get_user_model().objects.create(
            username='demo',
        )
        self.user.set_password('demo1234')
        self.user.save()

    def test_invalid_login(self):
        response = self.client.post(
            self.url,
            {'username': 'demo', 'password': 'invalid_password'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_login(self):
        response = self.client.post(
            self.url,
            {'username': 'demo', 'password': 'demo1234'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
