from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from rest_framework_security.authentication.serializers import LoginSerializer, LogoutSerializer


class PostApiViewMixin:
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(PostApiViewMixin, GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = ()


class LogoutAPIView(PostApiViewMixin, GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = ()
