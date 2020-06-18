from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_security.authentication.views import LoginAPIView, LogoutAPIView, UserSessionAPIView

router = DefaultRouter()
router.register('user_sessions', UserSessionAPIView)


urlpatterns = [
    url(r'^', include(router.urls)),
    path('login/', LoginAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
]
