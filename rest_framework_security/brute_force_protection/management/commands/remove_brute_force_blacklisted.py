from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Remove ip from bruce force protection blacklist"

    def add_arguments(self, parser):
        parser.add_argument("ip", type=str)

    def handle(self, *args, **options):
        from rest_framework_security.brute_force_protection.protection import (
            BruteForceProtection,
        )

        BruteForceProtection(options["ip"]).delete_ip()
