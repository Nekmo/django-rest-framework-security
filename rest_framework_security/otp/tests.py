import pyotp
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from rest_framework_security.otp.models import OTPDevice


class OTPDeviceViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        self.user: AbstractUser = get_user_model().objects.create(
            username='demo', last_login=timezone.now(),
        )

    def test_totp_create(self):
        req_data = {'otp_type': 'totp', 'destination_type': 'device'}
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('otpdevice-begin-register'),
                                    req_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        secret = response.json().get('uri').split('=')[1]
        code = pyotp.totp.TOTP(secret).now()
        response = self.client.post(reverse('otpdevice-list'),
                                    dict(req_data, data={'code': code}), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OTPDevice.objects.count(), 1)

    def test_totp_verify(self):
        otp_device = OTPDevice.objects.create(
            otp_type='totp', destination_type='device', data={'totp': pyotp.random_base32()}, user=self.user
        )
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('otpdevice-verify', kwargs={'pk': otp_device.pk}),
                                    {'code': pyotp.totp.TOTP(otp_device.data['totp']).now()}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.session['otp'], False)
