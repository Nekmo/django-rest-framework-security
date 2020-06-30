import pyotp
from rest_framework.exceptions import ValidationError

from rest_framework_security.otp import config


class EngineBase:
    def begin_register(self, request):
        raise NotImplementedError

    def confirm_register(self, request, validated_data):
        raise NotImplementedError

    def challenge(self, request, otp_device):
        raise NotImplementedError

    def verify(self, request, otp_device, data):
        raise NotImplementedError


class OTPEngineBase(EngineBase):
    keyname = ''

    def get_otp_instance(self, secret):
        raise NotImplementedError

    def begin_register(self, request):
        secret = pyotp.random_base32()
        request.session[self.keyname] = secret
        return self.get_otp_instance(secret).provisioning_uri(name=request.user.username,
                                                              issuer_name=config.OTP_NAME)

    def confirm_register(self, request, validated_data):
        validated_data = dict(validated_data)
        secret = request.session.pop(self.keyname, None)
        if not self.verify_otp(secret, validated_data['data']['code'], 1):
            raise ValidationError('Invalid code')
        validated_data['data'] = {self.keyname: secret}
        return validated_data

    def verify(self, request, otp_device, data):
        secret = otp_device.data[self.keyname]
        if not self.verify_otp(secret, data['code'], otp_device.counter):
            raise ValidationError('Invalid code')
        return {}

    def challenge(self, request, otp_device):
        return {'detail': "Not required"}

    def verify_otp(self, secret, code, counter=None):
        raise NotImplementedError

