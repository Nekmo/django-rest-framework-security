from django.conf import settings

ALLOW_IPS_DEFAULT_DEFAULT_IP_ACTION = ''

# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
