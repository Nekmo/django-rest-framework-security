from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_security.otp.views import (
    RegisterView,
    OTPDeviceViewSet,
    VerifyView,
    OTPStaticViewSet,
)

router = DefaultRouter()
router.register("otp_devices", OTPDeviceViewSet)
router.register("otp_statics", OTPStaticViewSet)


urlpatterns = [
    url(r"^", include(router.urls)),
    path("register/", RegisterView.as_view(), name="otp-register"),
    path("verify/", VerifyView.as_view(), name="otp-verify"),
]
