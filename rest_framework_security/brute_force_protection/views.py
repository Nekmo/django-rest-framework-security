from functools import wraps

from rest_framework import generics, views
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from rest_framework_security.brute_force_protection.exceptions import (
    BruteForceProtectionException,
)
from rest_framework_security.brute_force_protection.protection import (
    BruteForceProtection,
)
from rest_framework_security.brute_force_protection.serializers import (
    CaptchaSerializer,
    LoginProtectionSerializer,
)
from rest_framework_security.utils.ip import get_client_ip


def protect_api_request(only_on_error=False):
    def decorator(fn):
        @wraps(fn)
        def wrapped(self, request, *args, **kwargs):
            brute_force_protection = BruteForceProtection(get_client_ip(request))
            try:
                brute_force_protection.validate()
            except BruteForceProtectionException as e:
                raise PermissionDenied(detail=f"{e}")
            try:
                response = fn(self, request, *args, **kwargs)
            except ValidationError:
                brute_force_protection.increase_attempts()
                raise
            if not only_on_error or 500 > response.status_code >= 400:
                brute_force_protection.increase_attempts()
            return response

        return wrapped

    return decorator


class GetAPIView:
    def get(self, request, **kwargs):
        """"""
        return Response(
            self.serializer_class(context=self.get_serializer_context()).data
        )


class CaptchaViewSet(generics.CreateAPIView, GetAPIView, generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = CaptchaSerializer


class LoginProtectionViewSet(GetAPIView, generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = LoginProtectionSerializer
