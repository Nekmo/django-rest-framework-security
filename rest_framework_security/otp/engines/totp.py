import pyotp
from rest_framework.exceptions import ValidationError

from rest_framework_security.otp import config
from rest_framework_security.otp.engines.base import EngineBase


class TOTPEngine(EngineBase):
    def get_otp_instance(self, totp):
        return pyotp.totp.TOTP(totp)

    def begin_register(self, request):
        totp = pyotp.random_base32()
        request.session['totp'] = totp
        return self.get_otp_instance(totp).provisioning_uri(name=request.user.username,
                                                            issuer_name=config.OTP_NAME)

    def confirm_register(self, request, validated_data):
        validated_data = dict(validated_data)
        totp = request.session.pop('totp', None)
        if not self.get_otp_instance(totp).verify(validated_data['data']['code']):
            raise ValidationError('Invalid code')
        validated_data['data'] = {'totp': totp}
        return validated_data

    def challenge(self, request, otp_device):
        return {'detail': "Not required"}

    def verify(self, request, otp_device, data):
        totp = otp_device.data['totp']
        if not self.get_otp_instance(totp).verify(data['code']):
            raise ValidationError('Invalid code')
        return {}
