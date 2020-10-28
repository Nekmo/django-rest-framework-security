from rest_framework_security.allowed_ips import config
from rest_framework_security.emails import EmailBase


class OTPDeviceEmail(EmailBase):
    def __init__(self, user, device, connection=None, site_id=1):
        super(OTPDeviceEmail, self).__init__(user, connection, site_id)
        self.device = device

    def get_context(self):
        return dict(super(OTPDeviceEmail, self).get_context(),
                    device=self.device)

    @property
    def from_email(self):
        return config.ALLOWED_IPS_FROM_EMAIL or super(OTPDeviceEmail, self).from_email


class CreatedOTPDeviceEmail(OTPDeviceEmail):
    subject_template_name = 'otp/created_otp_device_subject.txt'
    email_template_name = 'otp/created_otp_device_email.txt'
    html_email_template_name = 'otp/created_otp_device_email.html'


class RemovedOTPDeviceEmail(OTPDeviceEmail):
    subject_template_name = 'otp/removed_otp_device_subject.txt'
    email_template_name = 'otp/removed_otp_device_email.txt'
    html_email_template_name = 'otp/removed_otp_device_email.html'
