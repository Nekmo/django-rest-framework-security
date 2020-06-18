from django.conf import settings

AUTHENTICATION_SESSION_AGE = 60 * 60 * 2
AUTHENTICATION_MAX_AGE = 60 * 60 * 24 * 2
AUTHENTICATION_REMEMBER_ME_SESSION_AGE = 60 * 60 * 24 * 2
AUTHENTICATION_REMEMBER_ME_MAX_AGE = 60 * 60 * 24 * 30
AUTHENTICATION_USER_SERIALIZER = ''


# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
