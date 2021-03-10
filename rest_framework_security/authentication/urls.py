from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_security.authentication.views import (
    LoginAPIView,
    LogoutAPIView,
    UserSessionAPIView,
    NextStepAPIView,
)

router = DefaultRouter()
router.register("user_sessions", UserSessionAPIView)


urlpatterns = [
    url(r"^", include(router.urls)),
    path("login/", LoginAPIView.as_view(), name="authentication-login"),
    path("logout/", LogoutAPIView.as_view(), name="authentication-logout"),
    path("next_steps/", NextStepAPIView.as_view(), name="authentication-next_steps"),
]
