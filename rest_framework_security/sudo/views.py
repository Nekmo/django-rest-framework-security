from rest_framework_security.sudo.expiration import get_expires_at
from rest_framework import permissions, generics
from rest_framework.response import Response

from rest_framework_security.sudo.serializers import (
    StatusSerializer,
    UpdateStatusSerializer,
    ExpireNowSerializer,
)


class StatusView(generics.GenericAPIView):
    """"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, **kwargs):
        """"""
        return Response(StatusSerializer(context=self.get_serializer_context()).data)


class UpdateStatusView(generics.CreateAPIView, generics.GenericAPIView):
    """"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateStatusSerializer

    def create(self, request, *args, **kwargs):
        super(UpdateStatusView, self).create(request, *args, **kwargs)
        return Response({"detail": f"Expires at {get_expires_at(request.user)}"})


class ExpireNowView(generics.CreateAPIView, generics.GenericAPIView):
    """"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExpireNowSerializer
