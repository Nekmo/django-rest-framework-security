from django.urls import path

from rest_framework_security.authentication.views import LoginAPIView, LogoutAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
]
