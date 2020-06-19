from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from rest_framework_security.deny_repeat_password import config

from rest_framework_security.deny_repeat_password.models import UserPassword


password_changed = Signal(providing_args=['user'])


@receiver(post_save, sender=get_user_model())
def set_user_password_receiver(sender, instance, **kwargs):
    user_password, created = UserPassword.objects.get_or_create(user=instance, password=instance.password)
    UserPassword.objects.remove_old_passwords(instance)
    if created:
        password_changed.send(None, user=instance)
