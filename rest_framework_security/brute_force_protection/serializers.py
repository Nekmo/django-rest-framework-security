from logging import getLogger

from captcha import client, _compat
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_framework_security.brute_force_protection import config
from rest_framework_security.brute_force_protection.exceptions import BruteForceProtectionBanException, \
    BruteForceProtectionException
from rest_framework_security.brute_force_protection.protection import BruteForceProtection
from rest_framework_security.brute_force_protection.utils import get_client_ip


logger = getLogger(__name__)


class CaptchaSerializer(serializers.Serializer):
    public_key = serializers.CharField(read_only=True)
    recaptcha_response = serializers.CharField(write_only=True)

    def get_initial(self):
        return {
            'public_key': config.BRUTE_FORCE_PROTECTION_RECAPTCHA_PUBLIC_KEY,
        }

    def create(self, validated_data):
        request = self.context['request']
        ip = get_client_ip(request)
        try:
            check_captcha = client.submit(
                recaptcha_response=validated_data['recaptcha_response'],
                private_key=self.private_key,
                remoteip=ip,
            )
        except _compat.HTTPError:  # Catch timeouts, etc
            raise ValidationError(
                self.error_messages["captcha_error"],
                code="captcha_error"
            )

        if not check_captcha.is_valid:
            logger.error(
                "ReCAPTCHA validation failed due to: %s" %
                check_captcha.error_codes
            )
            raise ValidationError(
                self.error_messages["captcha_invalid"],
                code="captcha_invalid"
            )
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
        except BruteForceProtectionException as e:
            status = 'failed'
            detail = f'{e}'
        else:
            status = 'valid'
        return {'status': status, 'detail': detail}
