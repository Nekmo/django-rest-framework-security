from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "List banned ips in brute force protection."

    def handle(self, *args, **options):
        from rest_framework_security.brute_force_protection.protection import (
            BruteForceProtection,
        )

        brute_force_protection = BruteForceProtection(None)
        self.stdout.write(
            "Banned IPs:\n" + "\n".join(brute_force_protection.list_failed_ips())
        )
        self.stdout.write(
            "\nSoft banned IPs:\n" + "\n".join(brute_force_protection.list_soft_ips())
        )
