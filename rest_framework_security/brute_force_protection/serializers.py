from logging import getLogger

from captcha import client, _compat
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_framework_security.brute_force_protection import config
from rest_framework_security.brute_force_protection.exceptions import BruteForceProtectionBanException, \
    BruteForceProtectionException, BruteForceProtectionCaptchaException
from rest_framework_security.brute_force_protection.protection import BruteForceProtection
from rest_framework_security.utils import get_client_ip
from django.utils.translation import ugettext_lazy as _


logger = getLogger(__name__)


class CaptchaSerializer(serializers.Serializer):
    public_key = serializers.CharField(read_only=True)
    recaptcha_response = serializers.CharField(write_only=True)

    def get_initial(self):
        return {
            'public_key': config.BRUTE_FORCE_PROTECTION_RECAPTCHA_PUBLIC_KEY,
        }

    def validate_recaptcha_response(self, recaptcha_response):
        request = self.context['request']
        ip = get_client_ip(request)
        try:
            check_captcha = client.submit(
                recaptcha_response=recaptcha_response,
                private_key=config.BRUTE_FORCE_PROTECTION_RECAPTCHA_PRIVATE_KEY,
                remoteip=ip,
            )
        except _compat.HTTPError:  # Catch timeouts, etc
            raise ValidationError(
                _("Error verifying reCAPTCHA, please try again."),
                code="captcha_error"
            )

        if not check_captcha.is_valid:
            logger.error(
                "ReCAPTCHA validation failed due to: %s" %
                check_captcha.error_codes
            )
            raise ValidationError(
                _("Error verifying reCAPTCHA, please try again."),
                code="captcha_invalid"
            )
        return ''

    def create(self, validated_data):
        request = self.context['request']
        ip = get_client_ip(request)
        BruteForceProtection(ip).set_soft_status(True)
        return self.get_initial()


class LoginProtectionSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    detail = serializers.CharField(read_only=True)

    def get_initial(self):
        request = self.context['request']
        ip = get_client_ip(request)
        detail = ''
        try:
            BruteForceProtection(ip).validate()
        except BruteForceProtectionBanException as e:
            status = 'banned'
            detail = f'{e}'
        except BruteForceProtectionCaptchaException as e:
            status = 'captcha_required'
            detail = f'{e}'
        else:
            status = 'allowed'
        return {'status': status, 'detail': detail}
