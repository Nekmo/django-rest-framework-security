import pyotp
from rest_framework_security.otp.engines.base import OTPEngineBase


class TOTPEngine(OTPEngineBase):
    keyname = 'totp'

    def get_otp_instance(self, secret):
        return pyotp.totp.TOTP(secret)

    def verify_otp(self, secret, code, counter=None):
        return self.get_otp_instance(secret).verify(code)
