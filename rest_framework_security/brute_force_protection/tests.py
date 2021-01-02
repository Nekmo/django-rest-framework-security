from unittest.mock import patch

from captcha import _compat
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class CaptchaViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('brute_force_protection-captcha')
        self.mock = patch('rest_framework_security.brute_force_protection.serializers.client')
        self.client_mocked = self.mock.start()

    def tearDown(self) -> None:
        self.mock.stop()

    def test_captcha_error(self):
        self.client_mocked.submit.side_effect = _compat.HTTPError('', 400, '', {'': ''}, None)
        response = self.client.post(self.url, {'recaptcha_response': 'foo'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('recaptcha_response')[0].code, 'captcha_error')

    def test_captcha_invalid(self):
        self.client_mocked.submit.return_value.is_valid = False
        response = self.client.post(self.url, {'recaptcha_response': 'foo'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('recaptcha_response')[0].code, 'captcha_invalid')

    def test_valid(self):
        response = self.client.post(self.url, {'recaptcha_response': 'foo'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
