from django.conf import settings

PERIODIC_PASSWORD_CHANGE_DAYS = 365
PERIODIC_PASSWORD_CHANGE_AUTHORIZED_URLS = []
PERIODIC_PASSWORD_CHANGE_MODEL = ""

# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
