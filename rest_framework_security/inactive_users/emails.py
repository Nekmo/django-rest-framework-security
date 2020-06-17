
from rest_framework_security.emails import EmailBase
from rest_framework_security.inactive_users import config


class InactiveUserAlertEmail(EmailBase):
    subject_template_name = 'inactive_users/inactive_user_alert_subject.txt'
    email_template_name = 'inactive_users/inactive_user_alert_email.txt'
    html_email_template_name = 'inactive_users/inactive_user_alert_email.txt'

    def __init__(self, user, connection=None, remaining_days=30, site_id=1):
        super(InactiveUserAlertEmail, self).__init__(user, connection, site_id)
        self.remaining_days = remaining_days

    def get_context(self):
        return dict(super(InactiveUserAlertEmail, self).get_context(),
                    remaining_days=self.remaining_days)

    @property
    def from_email(self):
        return config.INACTIVE_USERS_FROM_EMAIL or super(InactiveUserAlertEmail, self).from_email


class InactiveUserEmail(InactiveUserAlertEmail):
    subject_template_name = 'inactive_users/inactive_user_subject.txt'
    email_template_name = 'inactive_users/inactive_user_email.txt'
    html_email_template_name = 'inactive_users/inactive_user_email.txt'
