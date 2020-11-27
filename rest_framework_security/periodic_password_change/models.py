from django.db import models


class PeriodicPasswordChangeSettingsBase(models.Model):
    require_change_password = models.BooleanField(default=False)

    class Meta:
        abstract = True
