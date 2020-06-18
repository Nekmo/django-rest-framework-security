from django.db import models

from rest_framework_security.authentication.utils import get_session_store_class


class UserSessionQuerySet(models.QuerySet):
    def clean_and_delete(self):
        session_keys = self.values_list('session_key', flat=True)
        for session_key in session_keys:
            get_session_store_class()(session_key).delete()
        return self.delete()


class UserSessionManager(models.Manager):
    def get_queryset(self):
        return UserSessionQuerySet(self.model, using=self._db)

    def clean_and_delete(self):
        return self.get_queryset().clean_and_delete()
