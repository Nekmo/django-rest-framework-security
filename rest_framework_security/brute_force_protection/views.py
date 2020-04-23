from rest_framework import generics

from rest_framework_security.brute_force_protection.serializers import CaptchaSerializer, LoginProtectionSerializer


class CaptchaViewSet(generics.CreateAPIView, generics.RetrieveAPIView, generics.GenericAPIView):
    serializer_class = CaptchaSerializer


class LoginProtectionViewSet(generics.RetrieveAPIView, generics.GenericAPIView):
    serializer_class = LoginProtectionSerializer
