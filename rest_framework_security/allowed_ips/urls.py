from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_security.allowed_ips.views import UserIpConfigViewSet, UserIpViewSet

router = DefaultRouter()
router.register('user_ips', UserIpViewSet)
router.register('user_ip_configs', UserIpConfigViewSet, basename='user_ip_config')


urlpatterns = [
    url(r'^', include(router.urls)),
]
