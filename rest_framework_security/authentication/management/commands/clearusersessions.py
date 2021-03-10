from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to clean out expired user sessions"

    def handle(self, **options):
        from rest_framework_security.authentication.models import UserSession

        UserSession.objects.expired().clean_and_delete()
