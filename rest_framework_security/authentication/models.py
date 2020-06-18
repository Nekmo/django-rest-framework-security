from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.base import SessionBase
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework_security.authentication.managers import UserSessionManager
from rest_framework_security.authentication.utils import get_session_store_class


class UserSession(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='user_sessions')
    session_key = models.CharField(_('session key'), max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, max_length=64 * 1024)
    session_expires = models.DateTimeField()
    max_session_renewal = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserSessionManager()

    @property
    def session_store(self) -> SessionBase:
        return get_session_store_class()(self.session_key)

    def delete(self, **kwargs):
        self.session_store.delete()
        return super(UserSession, self).delete(**kwargs)

    class Meta:
        unique_together = ('user', 'session_key')
