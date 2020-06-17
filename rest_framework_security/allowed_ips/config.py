from django.conf import settings

ALLOWED_IPS_FROM_EMAIL = ''
ALLOWED_IPS_DEFAULT_IP_ACTION = 'warn'
ALLOWED_IPS_USER_IP_CONFIG_MODEL = ''
ALLOWED_IPS_PROFILE_URL = ''

# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
