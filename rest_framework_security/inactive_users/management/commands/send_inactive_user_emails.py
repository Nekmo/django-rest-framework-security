import datetime

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from rest_framework_security.inactive_users import config
from rest_framework_security.inactive_users.emails import InactiveUserAlertEmail


class Command(BaseCommand):
    help = 'Send inactive account alert emails to users'

    def add_arguments(self, parser):
        parser.add_argument('min-days', type=int, default=config.INACTIVE_USERS_MIN_DAYS,
                            help=_('Minimum days to send alert of inactive users.'))
        parser.add_argument('remaining-days', type=int, default=config.INACTIVE_USERS_REMAINING_DAYS,
                            help=_('remaining days to deactivate the account.'))

    def handle(self, *args, **options):
        user_class = get_user_model()
        dt = datetime.datetime.now() - datetime.timedelta(days=options['min_days'])
        users = user_class.objects.filter(last_login__lte=dt, is_active=True)
        with mail.get_connection() as connection:
            for user in users:
                InactiveUserAlertEmail(user, connection, remaining_days=options['remaining_days']).send()
