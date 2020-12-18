from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_security.allowed_ips.emails import DenyNewIpEmail, WarnNewIpEmail, WarnIpEmail
from rest_framework_security.allowed_ips.models import UserIp
from rest_framework_security.allowed_ips.protection import AllowedIpsProtection, get_default_ip_action


class AllowedIpsProtectionTestCase(TestCase):
    def setUp(self):
        self.ip = '1.1.1.1'
        self.user = get_user_model().objects.create(
            username='demo',
        )
        self.user_ip: UserIp = UserIp.objects.create(ip_address=self.ip, user=self.user, action='allow')

    def test_get_action_no_user(self):
        """If the user does not exist, return default action."""
        action, user_ip = AllowedIpsProtection(None, self.ip).get_action()
        self.assertEqual(action, get_default_ip_action(None))
        self.assertIsNone(user_ip)

    def test_get_action_user_ip(self):
        """Return action for the user ip."""
        action, user_ip = AllowedIpsProtection(self.user, self.ip).get_action()
        self.assertEqual(action, self.user_ip.action)
        self.assertEqual(user_ip, self.user_ip)

    @patch('rest_framework_security.allowed_ips.protection.get_default_ip_action', return_value='deny')
    def test_auth_failed(self, m):
        with self.assertRaises(PermissionDenied):
            AllowedIpsProtection(None, self.ip).auth_failed()
        m.assert_called_once()

    @patch('rest_framework_security.allowed_ips.protection.get_default_ip_action', return_value='deny')
    @patch.object(DenyNewIpEmail, 'send')
    def test_deny_new_ip(self, m1, m2):
        ip = '1.1.1.2'
        with self.assertRaises(PermissionDenied):
            AllowedIpsProtection(self.user, ip).successful_auth()
        user_ip = UserIp.objects.filter(user=self.user, ip_address=ip, action='').first()
        self.assertIsNotNone(user_ip)
        m1.assert_called_once()
        m2.assert_called_once()

    @patch.object(DenyNewIpEmail, 'send')
    def test_deny(self, m):
        self.user_ip.action = 'deny'
        self.user_ip.save()
        with self.assertRaises(PermissionDenied):
            AllowedIpsProtection(self.user, self.ip).successful_auth()
        m.assert_not_called()

    @patch('rest_framework_security.allowed_ips.protection.get_default_ip_action', return_value='warn')
    @patch.object(WarnNewIpEmail, 'send')
    def test_warn_new_ip(self, m1, m2):
        ip = '1.1.1.2'
        AllowedIpsProtection(self.user, ip).successful_auth()
        user_ip = UserIp.objects.filter(user=self.user, ip_address=ip, action='').first()
        self.assertIsNotNone(user_ip)
        m1.assert_called_once()
        m2.assert_called_once()

    @patch.object(WarnIpEmail, 'send')
    def test_warn(self, m):
        self.user_ip.action = 'warn'
        self.user_ip.save()
        AllowedIpsProtection(self.user, self.ip).successful_auth()
        m.assert_called_once()


class UserIpTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('userip-list')
        self.user = get_user_model().objects.create(
            username='demo',
        )
        self.other_user = get_user_model().objects.create(
            username='other',
        )

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        data = {'ip_address': '1.1.1.1', 'action': 'deny'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserIp.objects.count(), 1)
        self.assertEqual(UserIp.objects.get().user, self.user)
        self.assertEqual(UserIp.objects.get().ip_address, data['ip_address'])
        self.assertEqual(UserIp.objects.get().action, data['action'])

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        UserIp.objects.create(ip_address='1.1.1.1', user=self.user)
        UserIp.objects.create(ip_address='1.1.1.1', user=self.other_user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
