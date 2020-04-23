from django.urls import path

from rest_framework_security.brute_force_protection.views import CaptchaViewSet, LoginProtectionViewSet
from rest_framework_sudo.views import StatusView, UpdateStatusView, ExpireNowView

urlpatterns = [
    path('captcha/', CaptchaViewSet.as_view()),
    path('status/', LoginProtectionViewSet.as_view()),
]
