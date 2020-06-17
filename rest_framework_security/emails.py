from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template import loader


class EmailBase:
    subject_template_name = None
    email_template_name = None
    html_email_template_name = None

    def __init__(self, user, connection=None, site_id=1):
        self.user = user
        self.connection = connection
        self.site_id = site_id

    def get_context(self):
        return {
            'user': self.user,
            'site_name': self.site_name,
        }

    @property
    def site_name(self):
        return Site.objects.get(pk=self.site_id).name

    @property
    def from_email(self):
        return settings.DEFAULT_FROM_EMAIL

    @property
    def to_email(self):
        return self.user.email

    def send(self):
        context = self.get_context()
        subject = loader.render_to_string(self.subject_template_name, context)
        subject = subject.replace('\n', '')
        body = loader.render_to_string(self.email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, self.from_email, [self.to_email],
                                               connection=self.connection)
        if self.html_email_template_name is not None:
            html_email = loader.render_to_string(self.html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()
