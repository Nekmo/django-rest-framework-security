from django.db import models

from rest_framework_security.otp import config
from rest_framework_security.otp.exceptions import (
    OTPStaticTokensAlreadyExistsException,
    OTPDevicesRequiredException,
)


class OTPStaticQuerySet(models.QuerySet):
    def create_tokens(self, user):
        from rest_framework_security.otp.models import OTPDevice

        if self.filter(user=user).exists():
            raise OTPStaticTokensAlreadyExistsException(
                f"Static tokens have already been created for user {user}"
            )
        if not OTPDevice.objects.filter(user=user).exists():
            raise OTPDevicesRequiredException(
                "Create otp devices first to create static OTP tokens"
            )
        for i in range(config.OTP_STATIC_TOKENS):
            self.create(user=user)
        return self.filter(user=user)

    def use_token(self, user, token):
        static_token = self.filter(user=user, token=token).first()
        if static_token is None:
            raise self.model.DoesNotExist
        static_token.delete()


class OTPStaticManager(models.Manager):
    def get_queryset(self):
        return OTPStaticQuerySet(self.model, using=self._db)

    def create_tokens(self, user):
        return self.get_queryset().create_tokens(user)
