import datetime
from typing import Iterable, Union

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core import mail
from django.core.management.base import BaseCommand, CommandError
from django.db.models import QuerySet
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from rest_framework_security.periodic_password_change import config
from rest_framework_security.periodic_password_change.models import (
    PeriodicPasswordChangeSettingsBase,
)


class Command(BaseCommand):
    help = "Force change password on next authentication"

    def add_arguments(self, parser):
        parser.add_argument("user", type=str, help=_("Username, email or id."))

    def handle(self, *args, **options):
        if not config.PERIODIC_PASSWORD_CHANGE_MODEL:
            raise CommandError(
                "PERIODIC_PASSWORD_CHANGE_MODEL is undefined. To expire a user's "
                "password it is necessary to set the model."
            )
        user_identified: str = options["user"]
        model_class = import_string(config.PERIODIC_PASSWORD_CHANGE_MODEL)
        user_model: AbstractUser = get_user_model()
        user: Union[AbstractUser, None] = None
        if user_identified.isdigit():
            user = user_model.objects.filter(pk=user_identified).first()
        if user is None and "@" in user_identified:
            user = user_model.objects.filter(email=user_identified).first()
        if user is None:
            user = user_model.objects.filter(username=user_identified).first()
        if user is None:
            raise CommandError(f"User {user_identified} not found.")
        instance: PeriodicPasswordChangeSettingsBase = model_class.objects.get(
            user=user
        )
        instance.require_change_password = True
        instance.save()
