import base64
import os

import webauthn
from django.contrib.sites.models import Site
from rest_framework.exceptions import ValidationError
from webauthn.webauthn import AuthenticationRejectedException

from rest_framework_security.otp import config

RP_ID = config.OTP_DOMAIN
RP_NAME = config.OTP_NAME
ORIGIN = config.OTP_ORIGIN
CHALLENGE_DEFAULT_BYTE_LEN = 32


class WebAuthnEngine:
    def _get_rp_id(self, request):
        return RP_ID or request.META['HTTP_HOST'].split(':')[0]

    def _get_rp_name(self, request):
        return RP_NAME or Site.objects.get_current(request).name

    def _get_origin(self, request):
        return ORIGIN or f'{request.scheme}://{request.get_host()}'

    def begin_register(self, request):
        challenge = generate_challenge()
        request.session['challenge'] = challenge
        ukey = base64.urlsafe_b64encode(str(request.user.id).encode('utf-8'))
        make_credential_options = webauthn.WebAuthnMakeCredentialOptions(
            challenge, self._get_rp_name(request), self._get_rp_id(request), ukey, request.user.username,
            request.user.username, self._get_origin(request))
        return make_credential_options.registration_dict

    def confirm_register(self, request, validated_data):
        validated_data = dict(validated_data)
        challenge = request.session['challenge'].rstrip('=')
        webauthn_registration_response = webauthn.WebAuthnRegistrationResponse(
            self._get_rp_id(request),
            self._get_origin(request),
            validated_data['data'],
            challenge,
            'trusted_keys',  # directory
            trusted_attestation_cert_required=False,
            self_attestation_permitted=True,
            none_attestation_permitted=True,
            uv_required=False)  # User Verification
        webauthn_credential = webauthn_registration_response.verify()
        validated_data['data'] = {
            'pub_key': webauthn_credential.public_key.decode('utf-8'),
            'credential_id': webauthn_credential.credential_id.decode('utf-8'),
            'rp_id': self._get_rp_id(request),
            'icon_url': self._get_origin(request),
        }
        validated_data['counter'] = webauthn_credential.sign_count
        return validated_data

    def challenge(self, request, otp_device):
        challenge = generate_challenge()
        request.session['challenge'] = challenge

        ukey = base64.urlsafe_b64encode(str(request.user.id).encode('utf-8'))
        webauthn_user = webauthn.WebAuthnUser(
            ukey, otp_device.user.username, otp_device.user.username, otp_device.data['icon_url'],
            otp_device.data['credential_id'], otp_device.data['pub_key'],
            otp_device.counter, otp_device.data['rp_id'])

        webauthn_assertion_options = webauthn.WebAuthnAssertionOptions(
            webauthn_user, challenge)

        return webauthn_assertion_options.assertion_dict

    def verify(self, request, otp_device, data):
        challenge = request.session.get('challenge', '').rstrip('=')

        ukey = base64.urlsafe_b64encode(str(request.user.id).encode('utf-8'))
        webauthn_user = webauthn.WebAuthnUser(
            ukey, otp_device.user.username, otp_device.user.username, otp_device.data['icon_url'],
            otp_device.data['credential_id'], otp_device.data['pub_key'],
            otp_device.counter, otp_device.data['rp_id'])

        webauthn_assertion_response = webauthn.WebAuthnAssertionResponse(
            webauthn_user,
            data,
            challenge,
            self._get_origin(request),
            uv_required=False)  # User Verification
        try:
            sign_count = webauthn_assertion_response.verify()
        except AuthenticationRejectedException as e:
            raise ValidationError(str(e))
        otp_device.counter = sign_count
        otp_device.save()
        return {}


def generate_challenge(challenge_len=CHALLENGE_DEFAULT_BYTE_LEN):
    """Generate a challenge of challenge_len bytes, Base64-encoded.
    We use URL-safe base64, but we *don't* strip the padding, so that
    the browser can decode it without too much hassle.
    Note that if we are doing byte comparisons with the challenge in collectedClientData
    later on, that value will not have padding, so we must remove the padding
    before storing the value in the session.
    """
    # If we know Python 3.6 or greater is available, we could replace this with one
    # call to secrets.token_urlsafe
    challenge_bytes = os.urandom(challenge_len)
    challenge_base64 = base64.urlsafe_b64encode(challenge_bytes)
    # Python 2/3 compatibility: b64encode returns bytes only in newer Python versions
    if not isinstance(challenge_base64, str):
        challenge_base64 = challenge_base64.decode('utf-8')
    return challenge_base64
