from django.apps import AppConfig


class OTPApp(AppConfig):
    name = "rest_framework_security.otp"

    def ready(self):
        # noinspection PyUnresolvedReferences
        from rest_framework_security.otp import signals  # noqa
