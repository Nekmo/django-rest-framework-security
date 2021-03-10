from django.conf import settings

INACTIVE_USERS_FROM_EMAIL = ""
INACTIVE_USERS_MIN_DAYS = 365
INACTIVE_USERS_REMAINING_DAYS = 30

# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
