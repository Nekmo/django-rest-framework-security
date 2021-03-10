import os

from django.conf import settings

REST_FRAMEWORK_SECURITY_MAXMIND_LICENSE_KEY = ""
REST_FRAMEWORK_SECURITY_PROFILE_URL = ""

# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
