from django.apps import AppConfig


class DenyRepeatPasswordAppConfig(AppConfig):
    name = "rest_framework_security.deny_repeat_password"

    def ready(self):
        # noinspection PyUnresolvedReferences
        from rest_framework_security.deny_repeat_password import signals  # noqa
