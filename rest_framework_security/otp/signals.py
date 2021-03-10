from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from rest_framework_security.otp.emails import (
    CreatedOTPDeviceEmail,
    RemovedOTPDeviceEmail,
)
from rest_framework_security.otp.models import OTPDevice


@receiver(post_save, sender=OTPDevice)
def send_created_otp_device_email(sender, instance: OTPDevice, created, **kwargs):
    if created:
        CreatedOTPDeviceEmail(instance.user, instance).send()


@receiver(post_delete, sender=OTPDevice)
def send_removed_otp_device_email(sender, instance: OTPDevice, **kwargs):
    RemovedOTPDeviceEmail(instance.user, instance).send()
