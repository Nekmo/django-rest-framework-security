from datetime import timedelta
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from rest_framework_security.authentication.middleware import AuthenticationMiddleware
from rest_framework_security.authentication.models import UserSession


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


class LogoutAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('authentication-logout')
        self.user: AbstractUser = get_user_model().objects.create(
            username='demo',
        )

    @patch('rest_framework_security.authentication.serializers.logout')
    def test_logout(self, m):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m.assert_called_once()


class NextStepAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('authentication-next_steps')
        self.user: AbstractUser = get_user_model().objects.create(
            username='demo',
        )

    @patch('rest_framework_security.authentication.views.get_next_steps')
    def test_next_steps(self, m):
        next_step = Mock()
        next_step.is_required.return_value = True
        m.return_value = [next_step]
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserSession.objects.filter(user=self.user).count(), 0)


class UserSessionAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('usersession-list')
        self.user: AbstractUser = get_user_model().objects.create(
            username='demo',
        )
        self.other: AbstractUser = get_user_model().objects.create(
            username='other',
        )
        dt = timezone.now() + timedelta(days=1)
        UserSession.objects.create(
            user=self.user, session_key='a' * 40, ip_address='1.1.1.1',
            session_expires=dt, max_session_renewal=dt,
        )
        UserSession.objects.create(
            user=self.other, session_key='b' * 40, ip_address='1.1.1.2',
            session_expires=dt, max_session_renewal=dt,
        )

    def test_list(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_read_only(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_purge(self):
        url = reverse('usersession-purge')
        self.client.force_authenticate(self.user)
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserSession.objects.filter(user=self.user).count(), 0)


class AuthenticationMiddlewareTestCase(TestCase):
    def test_is_hijacked(self):
        get_response = Mock()
        request = Mock(**{'session.get.return_value': True})
        authentication_middleware = AuthenticationMiddleware(get_response)
        authentication_middleware.validate_and_renew_session = Mock()
        authentication_middleware.next_steps = Mock()
        authentication_middleware(request)
        authentication_middleware.next_steps.assert_not_called()

    def test_redirect(self):
        get_response = Mock()
        request = Mock(**{'session.get.return_value': False})
        authentication_middleware = AuthenticationMiddleware(get_response)
        authentication_middleware.validate_and_renew_session = Mock()
        authentication_middleware.next_steps = Mock(return_value=True)
        self.assertTrue(authentication_middleware(request))
        authentication_middleware.next_steps.assert_called_once()
