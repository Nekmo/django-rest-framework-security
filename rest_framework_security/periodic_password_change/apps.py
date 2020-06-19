from django.apps import AppConfig


class PeriodicPasswordChangeApp(AppConfig):
    name = 'rest_framework_security.periodic_password_change'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from rest_framework_security.periodic_password_change import signals  # noqa
