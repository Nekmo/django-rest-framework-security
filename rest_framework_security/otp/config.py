from django.conf import settings

OTP_DOMAIN = None
OTP_NAME = None
OTP_ORIGIN = None
OTP_STATIC_TOKENS = 20
OTP_USER_ENABLED = True
OTP_FROM_EMAIL = ''

# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
