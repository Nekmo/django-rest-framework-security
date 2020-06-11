from django.conf import settings

DENY_REPEAT_PASSWORD_MAX_SAVED_PASSWORDS = 10


# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
