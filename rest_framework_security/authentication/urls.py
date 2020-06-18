from django.urls import path

from rest_framework_security.authentication.views import LoginAPIView


urlpatterns = [
    path('login', LoginAPIView.as_view()),
]
