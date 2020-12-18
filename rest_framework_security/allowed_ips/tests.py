from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework_security.allowed_ips.models import UserIp
from rest_framework_security.allowed_ips.protection import AllowedIpsProtection, get_default_ip_action


class AllowedIpsProtectionTestCase(TestCase):
    def setUp(self):
        self.ip = '1.1.1.1'
        self.user = get_user_model().objects.create(
            username='demo',
        )

    def test_get_action_no_user(self):
        """If the user does not exist, return default action."""
        action, user_ip = AllowedIpsProtection(None, self.ip).get_action()
        self.assertEqual(action, get_default_ip_action(None))
        self.assertIsNone(user_ip)

    def test_get_action_user_ip(self):
        """Return action for the user ip."""
        created_user_ip = UserIp.objects.create(ip_address=self.ip, user=self.user, action='allow')
        action, user_ip = AllowedIpsProtection(self.user, self.ip).get_action()
        self.assertEqual(action, created_user_ip.action)
        self.assertEqual(user_ip, created_user_ip)
