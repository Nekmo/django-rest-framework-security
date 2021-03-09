from unittest.mock import patch

from captcha import _compat
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from rest_framework_security.brute_force_protection import config
from rest_framework_security.brute_force_protection.protection import (
    BruteForceProtection,
)


class CaptchaViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("brute_force_protection-captcha")
        self.mock = patch(
            "rest_framework_security.brute_force_protection.serializers.client"
        )
        self.client_mocked = self.mock.start()

    def tearDown(self) -> None:
        self.mock.stop()

    def test_captcha_error(self):
        self.client_mocked.submit.side_effect = _compat.HTTPError(
            "", 400, "", {"": ""}, None
        )
        response = self.client.post(
            self.url, {"recaptcha_response": "foo"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("recaptcha_response")[0].code, "captcha_error"
        )

    def test_captcha_invalid(self):
        self.client_mocked.submit.return_value.is_valid = False
        response = self.client.post(
            self.url, {"recaptcha_response": "foo"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("recaptcha_response")[0].code, "captcha_invalid"
        )

    def test_valid(self):
        response = self.client.post(
            self.url, {"recaptcha_response": "foo"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginProtectionViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("brute_force_protection-status")

    def test_allowed(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("status"), "allowed")

    def test_banned(self):
        protection = BruteForceProtection("127.0.0.1")
        protection.delete_ip()
        for i in range(config.BRUTE_FORCE_PROTECTION_BAN_LIMIT):
            protection.increase_attempts()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("status"), "banned")

    def test_captcha_required(self):
        protection = BruteForceProtection("127.0.0.1")
        protection.delete_ip()
        for i in range(config.BRUTE_FORCE_PROTECTION_SOFT_LIMIT):
            protection.increase_attempts()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("status"), "captcha_required")
