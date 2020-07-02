from django.shortcuts import redirect
from django.urls import reverse

from rest_framework_security.authentication.next_steps import NextStepBase
from rest_framework_security.otp import config


class NextStep(NextStepBase):
    step_name = 'otp'

    def get_allowed_urls(self):
        return [
            'otpdevice-verify',
            'otpdevice-challenge',
            'otpdevice-list',
            'otpdevice-detail',
            'otpstatic-use-token',
            reverse('otp-verify'),
        ]

    def get_admin_redirect(self):
        return redirect('otp-verify')

    def is_required(self, request):
        from rest_framework_security.otp.models import OTPDevice
        return self.is_active(request) is not False and \
            config.OTP_USER_ENABLED and OTPDevice.objects.filter(user=request.user).exists()
