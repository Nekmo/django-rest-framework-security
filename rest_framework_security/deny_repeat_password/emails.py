from rest_framework_security.deny_repeat_password import config
from rest_framework_security.emails import EmailBase


class ChangedPasswordEmail(EmailBase):
    subject_template_name = 'deny_repeat_password/changed_password_subject.txt'
    email_template_name = 'deny_repeat_password/changed_password_email.txt'
    html_email_template_name = 'deny_repeat_password/changed_password_email.html'

    def get_context(self):
        return dict(
            super(ChangedPasswordEmail, self).get_context(),
            profile_url=config.DENY_REPEAT_PASSWORD_PROFILE_URL,
        )

    @property
    def from_email(self):
        return config.DENY_REPEAT_PASSWORD_FROM_EMAIL or super(ChangedPasswordEmail, self).from_email
