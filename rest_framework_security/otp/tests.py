from unittest.mock import Mock, patch

import pyotp
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from rest_framework_security.otp import config
from rest_framework_security.otp.models import OTPDevice, OTPStatic
from rest_framework_security.otp.views import PngRenderer


class OTPDeviceViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        self.user: AbstractUser = get_user_model().objects.create(
            username="demo",
            last_login=timezone.now(),
        )

    def test_png(self):
        req_data = {"otp_type": "totp", "destination_type": "device"}
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("otpdevice-begin-register"),
            req_data,
            format="png",
            HTTP_ACCEPT="image/png",
        )
        self.assertIsInstance(response.accepted_renderer, PngRenderer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_totp_create(self):
        req_data = {"otp_type": "totp", "destination_type": "device"}
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("otpdevice-begin-register"), req_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        secret = response.json().get("uri").split("=")[1]
        code = pyotp.totp.TOTP(secret).now()
        response = self.client.post(
            reverse("otpdevice-list"),
            dict(req_data, data={"code": code}),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OTPDevice.objects.count(), 1)

    def test_totp_verify(self):
        otp_device = OTPDevice.objects.create(
            otp_type="totp",
            destination_type="device",
            data={"totp": pyotp.random_base32()},
            user=self.user,
        )
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("otpdevice-verify", kwargs={"pk": otp_device.pk}),
            {"code": pyotp.totp.TOTP(otp_device.data["totp"]).now()},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.session["otp"], False)

    def test_hotp_create(self):
        req_data = {"otp_type": "hotp", "destination_type": "device"}
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("otpdevice-begin-register"), req_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        secret = response.json().get("uri").split("=")[1].split("&")[0]
        code = pyotp.hotp.HOTP(secret).at(1)
        response = self.client.post(
            reverse("otpdevice-list"),
            dict(req_data, data={"code": code}),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OTPDevice.objects.count(), 1)

    def test_hotp_verify(self):
        otp_device = OTPDevice.objects.create(
            otp_type="hotp",
            destination_type="device",
            data={"hotp": pyotp.random_base32()},
            user=self.user,
        )
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("otpdevice-verify", kwargs={"pk": otp_device.pk}),
            {"code": pyotp.hotp.HOTP(otp_device.data["hotp"]).at(0)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.session["otp"], False)

    @patch(
        "rest_framework_security.otp.engines.webauthn.webauthn.WebAuthnRegistrationResponse"
    )
    def test_webauthn_create(self, m):
        m.return_value.verify.return_value.public_key = b""
        m.return_value.verify.return_value.credential_id = b""
        m.return_value.verify.return_value.sign_count = 0
        req_data = {"otp_type": "webauthn", "destination_type": "device"}
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("otpdevice-begin-register"),
            req_data,
            HTTP_HOST="127.0.0.1",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            reverse("otpdevice-list"),
            dict(
                req_data,
                data={"pub_key": "", "credential_id": "", "rp_id": "", "icon_url": ""},
            ),
            HTTP_HOST="127.0.0.1",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OTPDevice.objects.count(), 1)

    @patch("rest_framework_security.otp.engines.webauthn.webauthn")
    def test_webauthn_verify(self, m):
        m.WebAuthnAssertionOptions.return_value = Mock(unsafe=True)
        m.WebAuthnAssertionOptions.return_value.assertion_dict = {}
        m.WebAuthnAssertionResponse.return_value.verify.return_value = 0  # counter
        otp_device = OTPDevice.objects.create(
            otp_type="webauthn",
            destination_type="device",
            data={"pub_key": "", "credential_id": "", "rp_id": "", "icon_url": ""},
            user=self.user,
        )
        self.client.force_authenticate(self.user)
        self.client.get(
            reverse("otpdevice-challenge", kwargs={"pk": otp_device.pk}),
            {},
            format="json",
        )
        response = self.client.post(
            reverse("otpdevice-verify", kwargs={"pk": otp_device.pk}), {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.session["otp"], False)


class OTPStaticViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        self.user: AbstractUser = get_user_model().objects.create(
            username="demo",
            last_login=timezone.now(),
        )

    def test_create_otp_device_before(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse("otpstatic-create-tokens"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_static_tokens_exists(self):
        OTPDevice.objects.create(
            otp_type="totp",
            destination_type="device",
            data={"totp": pyotp.random_base32()},
            user=self.user,
        )
        OTPStatic.objects.create(
            user=self.user,
            token="0" * 16,
        )
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse("otpstatic-create-tokens"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_static_tokens(self):
        OTPDevice.objects.create(
            otp_type="totp",
            destination_type="device",
            data={"totp": pyotp.random_base32()},
            user=self.user,
        )
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse("otpstatic-create-tokens"), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), config.OTP_STATIC_TOKENS)

    def test_use_static_token(self):
        otp_static = OTPStatic.objects.create(
            user=self.user,
            token="0" * 8,
        )
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("otpstatic-use-token"), {"token": otp_static.token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(OTPStatic.objects.count(), 0)
        self.assertEqual(self.client.session["otp"], False)

    def test_use_invalid_static_token(self):
        OTPStatic.objects.create(
            user=self.user,
            token="0" * 8,
        )
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("otpstatic-use-token"), {"token": "invalid"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
