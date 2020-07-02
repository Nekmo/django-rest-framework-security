from django.apps import AppConfig


class AuthenticationApp(AppConfig):
    name = 'rest_framework_security.authentication'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from rest_framework_security.authentication import signals  # noqa
