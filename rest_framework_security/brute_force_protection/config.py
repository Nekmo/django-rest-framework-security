from django.conf import settings

BRUTE_FORCE_PROTECTION_CACHE_PREFIX = "brute_force"
BRUTE_FORCE_PROTECTION_EXPIRATION = 60 * 60 * 2
BRUTE_FORCE_PROTECTION_SOFT_LIMIT = 2
BRUTE_FORCE_PROTECTION_SOFT_EXPIRATION = 60
BRUTE_FORCE_PROTECTION_BAN_LIMIT = 6
BRUTE_FORCE_PROTECTION_RECAPTCHA_PUBLIC_KEY = ""
BRUTE_FORCE_PROTECTION_RECAPTCHA_PRIVATE_KEY = ""


# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
