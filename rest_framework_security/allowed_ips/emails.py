from rest_framework_security.allowed_ips import config
from rest_framework_security import config as global_config
from rest_framework_security.emails import EmailBase


class WarnNewIpEmail(EmailBase):
    subject_template_name = 'allowed_ips/warn_new_ip_subject.txt'
    email_template_name = 'allowed_ips/warn_new_ip_email.txt'
    html_email_template_name = 'allowed_ips/warn_new_ip_email.html'

    def __init__(self, user, ip, connection=None, site_id=1):
        super(WarnNewIpEmail, self).__init__(user, connection, site_id)
        self.ip = ip

    def get_context(self):
        return dict(super(WarnNewIpEmail, self).get_context(),
                    profile_url=config.ALLOWED_IPS_PROFILE_URL or global_config.REST_FRAMEWORK_SECURITY_PROFILE_URL,
                    ip=self.ip)

    @property
    def from_email(self):
        return config.ALLOWED_IPS_FROM_EMAIL or super(WarnNewIpEmail, self).from_email


class WarnIpEmail(WarnNewIpEmail):
    subject_template_name = 'allowed_ips/warn_ip_subject.txt'
    email_template_name = 'allowed_ips/warn_ip_email.txt'
    html_email_template_name = 'allowed_ips/warn_ip_email.html'


class DenyNewIpEmail(WarnNewIpEmail):
    subject_template_name = 'allowed_ips/deny_new_ip_subject.txt'
    email_template_name = 'allowed_ips/deny_new_ip_email.txt'
    html_email_template_name = 'allowed_ips/deny_new_ip_email.html'
