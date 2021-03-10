from bitfield import BitField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _


CALENDAR_ACTIONS = [
    ("allow", _("Allow access")),
    ("req_2fa", _("Require multi-factor authentication")),
    ("warn", _("Allow but send email")),
    ("deny", _("Deny access")),
]


class UserCalendar(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    action = models.CharField(max_length=12, choices=CALENDAR_ACTIONS)
    date_start_at = models.DateField(blank=True, null=True, db_index=True)
    date_end_at = models.DateField(blank=True, null=True, db_index=True)
    time_start_at = models.TimeField(blank=True, null=True, db_index=True)
    time_end_at = models.TimeField(blank=True, null=True, db_index=True)

    # Alternative: https://github.com/disqus/django-bitfield
    monday = models.BooleanField(default=True, db_index=True)
    tuesday = models.BooleanField(default=True, db_index=True)
    wednesday = models.BooleanField(default=True, db_index=True)
    thursday = models.BooleanField(default=True, db_index=True)
    friday = models.BooleanField(default=True, db_index=True)
    saturday = models.BooleanField(default=True, db_index=True)
    sunday = models.BooleanField(default=True, db_index=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserCalendarSettings(models.Model):
    default_calendar_action = models.CharField(max_length=12, choices=CALENDAR_ACTIONS)

    class Meta:
        abstract = True
