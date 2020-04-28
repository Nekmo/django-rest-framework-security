from django.contrib.gis.db import models


class PasswordChangeSettings(models.Model):
    password_changed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
