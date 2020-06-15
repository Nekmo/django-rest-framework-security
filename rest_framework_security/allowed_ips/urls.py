from django.urls import path

from rest_framework_security.allowed_ips.models import UserIp
from rest_framework_security.allowed_ips.views import UserIpConfigViewSet


urlpatterns = [
    path('user_ips/', UserIp.as_view()),
    path('user_ip_configs/', UserIpConfigViewSet.as_view()),
]
