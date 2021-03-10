from django.urls import path

from rest_framework_security.brute_force_protection.views import (
    CaptchaViewSet,
    LoginProtectionViewSet,
)

urlpatterns = [
    path("captcha/", CaptchaViewSet.as_view(), name="brute_force_protection-captcha"),
    path(
        "status/",
        LoginProtectionViewSet.as_view(),
        name="brute_force_protection-status",
    ),
]
