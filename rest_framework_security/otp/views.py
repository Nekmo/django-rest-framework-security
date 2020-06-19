from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_framework_security.otp.models import OTPDevice
from rest_framework_security.otp.serializers import OTPDeviceSerializer
from rest_framework_security.views import IsOwnerViewSetMixin


class OTPDeviceAPIView(IsOwnerViewSetMixin, viewsets.mixins.DestroyModelMixin, ReadOnlyModelViewSet):
    serializer_class = OTPDeviceSerializer
    permission_classes = (IsAuthenticated,)
    queryset = OTPDevice.objects.all()
