import datetime

from django.conf import settings

REST_FRAMEWORK_SUDO_EXPIRATION = datetime.timedelta(minutes=10)

for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
