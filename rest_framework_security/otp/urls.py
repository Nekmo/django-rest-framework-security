from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_security.otp.views import YubikeyView, OTPDeviceViewSet, VerifyView, OTPStaticViewSet

router = DefaultRouter()
router.register('otp_devices', OTPDeviceViewSet)
router.register('otp_statics', OTPStaticViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    path('yubikey/', YubikeyView.as_view()),
    path('verify/', VerifyView.as_view()),
]
