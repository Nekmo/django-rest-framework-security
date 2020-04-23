from rest_framework import generics, views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rest_framework_security.brute_force_protection.serializers import CaptchaSerializer, LoginProtectionSerializer


class GetAPIView:
    def get(self, request, **kwargs):
        """
        """
        return Response(self.serializer_class(context=self.get_serializer_context()).data)


class CaptchaViewSet(generics.CreateAPIView, GetAPIView, generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = CaptchaSerializer


class LoginProtectionViewSet(GetAPIView, generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = LoginProtectionSerializer
