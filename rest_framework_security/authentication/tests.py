from datetime import timedelta
from unittest.mock import patch, Mock, MagicMock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.test import TestCase
from django.urls import NoReverseMatch
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from rest_framework_security.authentication.middleware import AuthenticationMiddleware, get_admin_base_url
from rest_framework_security.authentication.models import UserSession
from rest_framework_security.authentication.next_steps import NextStepBase


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

    @patch('rest_framework_security.authentication.middleware.get_next_steps')
    def test_next_steps_admin_url(self, m):
        admin_url = '/admin/url/'
        next_step = NextStepBase()
        next_step.is_required = Mock(return_value=True)
        next_step.get_admin_redirect = Mock(return_value=admin_url)
        next_step.step_name = 'test'
        m.return_value = [next_step]
        authentication_middleware = AuthenticationMiddleware(None)
        request_mock = Mock()
        request_mock.session = {}
        self.assertEqual(authentication_middleware.next_steps(request_mock), admin_url)
        self.assertEqual(request_mock.session.get('test'), True)

    @patch('rest_framework_security.authentication.middleware.get_next_steps')
    def test_next_steps_required(self, m):
        next_step = NextStepBase()
        next_step.is_required = Mock(return_value=True)
        m.return_value = [next_step]
        authentication_middleware = AuthenticationMiddleware(None)
        request_mock = Mock()
        request_mock.session = {}
        authentication_middleware.next_steps(request_mock)
        self.assertEqual(request_mock.user, AnonymousUser())

    @patch('rest_framework_security.authentication.middleware.get_next_steps')
    @patch('rest_framework_security.authentication.middleware.is_path_allowed', return_value=True)
    def test_next_steps_path_allowed(self, m1, m2):
        next_step = NextStepBase()
        next_step.is_required = Mock(return_value=True)
        m2.return_value = [next_step]
        authentication_middleware = AuthenticationMiddleware(None)
        request_mock = Mock()
        request_mock.session = {}
        authentication_middleware.next_steps(request_mock)
        self.assertEqual(request_mock.user, request_mock.user)

    @patch('rest_framework_security.authentication.middleware.logout')
    def test_validate_and_renew_session_logout(self, m):
        authentication_middleware = AuthenticationMiddleware(None)
        request_mock = Mock(**{'META.get.return_value': 'new_ip'})
        authentication_middleware.validate_and_renew_session(request_mock, {'ip_address': 'old_ip'})
        m.assert_called_once()

    def test_validate_and_renew_session_not_authenticated(self):
        authentication_middleware = AuthenticationMiddleware(None)
        request_mock = Mock(**{'user.is_authenticated': False})
        authentication_middleware.validate_and_renew_session(request_mock, {})

    @patch('rest_framework_security.authentication.middleware.get_client_ip', return_value='1.1.1.1')
    def test_validate_and_renew_session_expired(self, m):
        user: AbstractUser = get_user_model().objects.create(
            username='demo',
        )
        ip_address = '1.1.1.1'
        session_key = 'a' * 40
        dt = timezone.now() + timedelta(minutes=1)
        user_session = UserSession.objects.create(
            user=user, session_key=session_key, ip_address=ip_address,
            session_expires=dt, max_session_renewal=dt,
        )
        authentication_middleware = AuthenticationMiddleware(None)
        request_mock = Mock()
        request_mock.user = user
        session = {
            'ip_address': ip_address,
            'session_updated_at': (timezone.now() - timedelta(days=1)).isoformat(),
            'max_session_renewal': dt.isoformat(),
        }
        session_mock = MagicMock()
        session_mock.get.side_effect = session.get
        session_mock.session_key = session_key
        authentication_middleware.validate_and_renew_session(request_mock, session_mock)
        self.assertGreater(
            UserSession.objects.get(pk=user_session.pk).session_expires,
            dt
        )


class NextStepBaseTestCase(TestCase):
    def test_title(self):
        self.assertEqual(NextStepBase().title, '')

    def test_description(self):
        self.assertEqual(NextStepBase().description, '')


class GetAdminBaseUrlTestCase(TestCase):
    @patch('rest_framework_security.authentication.next_steps.reverse', return_value='/admin/')
    def test_reverse(self, m):
        self.assertEqual(get_admin_base_url(), '/admin/')

    @patch('rest_framework_security.authentication.next_steps.reverse', side_effect=NoReverseMatch)
    def test_reverse_none(self, m):
        self.assertEqual(get_admin_base_url(), None)
