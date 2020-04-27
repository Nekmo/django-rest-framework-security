from django.core.cache import cache
from rest_framework_security.brute_force_protection import config
from rest_framework_security.brute_force_protection.exceptions import BruteForceProtectionException, \
    BruteForceProtectionBanException, BruteForceProtectionCaptchaException


class BruteForceProtection:
    def __init__(self, ip):
        self.ip = ip

    def get_cache_attemps_key(self):
        return f'{config.BRUTE_FORCE_PROTECTION_CACHE_PREFIX}:failed:ip:{self.ip}'

    def get_cache_soft_key(self):
        return f'{config.BRUTE_FORCE_PROTECTION_CACHE_PREFIX}:soft:ip:{self.ip}'

    def get_attempts(self):
        return cache.get(self.get_cache_attemps_key(), default=0)

    def get_soft_status(self):
        return cache.get(self.get_cache_soft_key(), default=False)

    def set_soft_status(self, value):
        cache.set(self.get_cache_soft_key(), value,
                  config.BRUTE_FORCE_PROTECTION_SOFT_EXPIRATION)

    def increase_attempts(self):
        key = self.get_cache_attemps_key()
        cache.add(key, 0, config.BRUTE_FORCE_PROTECTION_EXPIRATION)
        cache.incr(key)
        self.set_soft_status(False)

    def validate(self):
        attemps = self.get_attempts()
        if attemps >= config.BRUTE_FORCE_PROTECTION_BAN_LIMIT:
            raise BruteForceProtectionBanException('Your ip has been banned after several login attempts.')
        if attemps >= config.BRUTE_FORCE_PROTECTION_SOFT_LIMIT and not self.get_soft_status():
            raise BruteForceProtectionCaptchaException('Captcha is mandatory')
