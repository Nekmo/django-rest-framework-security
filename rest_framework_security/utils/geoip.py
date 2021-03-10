from geoip2_tools.manager import Geoip2DataBaseManager

from rest_framework_security import config

geoip2_manager = Geoip2DataBaseManager(
    config.REST_FRAMEWORK_SECURITY_MAXMIND_LICENSE_KEY
)
