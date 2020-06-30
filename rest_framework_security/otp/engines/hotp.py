import pyotp
from rest_framework_security.otp.engines.base import OTPEngineBase


class HOTPEngine(OTPEngineBase):
    keyname = 'hotp'

    def get_otp_instance(self, secret):
        return pyotp.hotp.HOTP(secret)

    def confirm_register(self, request, validated_data):
        validated_data = super(HOTPEngine, self).confirm_register(request, validated_data)
        validated_data['counter'] = 2
        return validated_data

    def verify(self, request, otp_device, data):
        verified = super(HOTPEngine, self).verify(request, otp_device, data)
        otp_device.counter += 1
        otp_device.save()
        return verified

    def verify_otp(self, secret, code, counter=None):
        return self.get_otp_instance(secret).verify(code, counter)
