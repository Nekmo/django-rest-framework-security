from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template import loader

from rest_framework_security.inactive_users import config


class InactiveUserAlertEmail(object):
    subject_template_name = 'inactive_users/inactive_user_alert_subject.txt'
    email_template_name = 'inactive_users/inactive_user_alert_email.txt'
    html_email_template_name = 'inactive_users/inactive_user_alert_email.txt'

    def __init__(self, user, connection=None, remaining_days=30, site_id=1):
        self.user = user
        self.connection = connection
        self.remaining_days = remaining_days
        self.site_id = site_id

    def get_context(self):
        return {
            'user': self.user,
            'site_name': self.site_name,
            'remaining_days': self.remaining_days,
        }

    @property
    def site_name(self):
        return Site.objects.get(pk=self.site_id).name

    @property
    def from_email(self):
        return config.INACTIVE_USERS_FROM_EMAIL or settings.DEFAULT_FROM_EMAIL

    @property
    def to_email(self):
        return self.user.email

    def send(self):
        context = self.get_context()
        subject = loader.render_to_string(self.subject_template_name, context)
        body = loader.render_to_string(self.email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, self.from_email, [self.to_email],
                                               connection=self.connection)
        if self.html_email_template_name is not None:
            html_email = loader.render_to_string(self.html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()


class InactiveUserEmail(InactiveUserAlertEmail):
    subject_template_name = 'inactive_users/inactive_user_subject.txt'
    email_template_name = 'inactive_users/inactive_user_email.txt'
    html_email_template_name = 'inactive_users/inactive_user_email.txt'
