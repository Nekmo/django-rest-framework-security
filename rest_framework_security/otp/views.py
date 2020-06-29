import webauthn
from django.views.generic import TemplateView
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_framework_security.otp.forms import SelectOTPDeviceForm
from rest_framework_security.otp.models import OTPDevice, get_engine
from rest_framework_security.otp.serializers import OTPDeviceSerializer, OTPDeviceBeginRegisterSerializer, \
    OTPDeviceCreateSerializer
from rest_framework_security.views import IsOwnerViewSetMixin


class OTPDeviceViewSet(IsOwnerViewSetMixin, viewsets.mixins.DestroyModelMixin, viewsets.mixins.CreateModelMixin,
                       ReadOnlyModelViewSet):
    serializer_class = OTPDeviceSerializer
    permission_classes = (IsAuthenticated,)
    queryset = OTPDevice.objects.all()

    def get_serializer_class(self):
        if self.action == 'begin_register':
            return OTPDeviceBeginRegisterSerializer
        elif self.action == 'create':
            return OTPDeviceCreateSerializer
        elif self.action == 'verify':
            return serializers.Serializer
        return super(OTPDeviceViewSet, self).get_serializer_class()

    @action(detail=False, methods=['POST'])
    def begin_register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        engine = get_engine(serializer.validated_data['otp_type'])
        return Response(engine.begin_register(request))

    @action(detail=True, methods=['GET'])
    def challenge(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.get_engine().challenge(request, instance))

    @action(detail=True, methods=['POST'])
    def verify(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.get_engine().verify(request, instance, request.data))


class YubikeyView(TemplateView):
    template_name = 'otp/yubikey.html'


class VerifyView(TemplateView):
    template_name = 'otp/verify.html'

    def get_context_data(self, **kwargs):
        context = super(VerifyView, self).get_context_data(**kwargs)
        context['form'] = SelectOTPDeviceForm(user=self.request.user)
        return context
