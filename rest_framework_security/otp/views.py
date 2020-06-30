import io

import qrcode
from django.http import Http404
from django.views.generic import TemplateView
from rest_framework import viewsets, serializers, renderers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from rest_framework_security.otp.exceptions import OTPException
from rest_framework_security.otp.forms import SelectOTPDeviceForm
from rest_framework_security.otp.models import OTPDevice, get_engine, OTPStatic
from rest_framework_security.otp.serializers import OTPDeviceSerializer, OTPDeviceBeginRegisterSerializer, \
    OTPDeviceCreateSerializer, OTPStaticSerializer, OTPStaticObfuscatedSerializer
from rest_framework_security.views import IsOwnerViewSetMixin


class PngRenderer(renderers.BaseRenderer):
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        image = qrcode.make(data)
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format='PNG')
        return imgByteArr.getvalue()


class OTPDeviceViewSet(IsOwnerViewSetMixin, viewsets.mixins.DestroyModelMixin, viewsets.mixins.CreateModelMixin,
                       ReadOnlyModelViewSet):
    serializer_class = OTPDeviceSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PngRenderer]
    queryset = OTPDevice.objects.all()

    def get_serializer_class(self):
        if self.action == 'begin_register':
            return OTPDeviceBeginRegisterSerializer
        elif self.action == 'create':
            return OTPDeviceCreateSerializer
        elif self.action == 'verify':
            return serializers.Serializer
        return super(OTPDeviceViewSet, self).get_serializer_class()

    @action(detail=False, methods=['POST', 'GET'])
    def begin_register(self, request, *args, **kwargs):
        data = request.GET if request.method == 'GET' else request.data
        serializer = self.get_serializer(data=data)
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


class OTPStaticViewSet(IsOwnerViewSetMixin, viewsets.mixins.ListModelMixin, GenericViewSet):
    serializer_class = OTPStaticObfuscatedSerializer
    queryset = OTPStatic.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['create_tokens', 'use_token']:
            return OTPStaticSerializer
        else:
            return super(OTPStaticViewSet, self).get_serializer_class()

    @action(detail=False, methods=['POST'])
    def create_tokens(self, request, *args, **kwargs):
        try:
            self.get_queryset().create_tokens(request.user)
        except OTPException as e:
            raise ValidationError(f'{e}')
        return self.list(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def use_token(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.get_queryset().use_token(request.user, serializer.validated_data['token'])
        except self.get_queryset().model.DoesNotExist:
            raise Http404
        return Response(status=status.HTTP_204_NO_CONTENT)


class YubikeyView(TemplateView):
    template_name = 'otp/yubikey.html'


class VerifyView(TemplateView):
    template_name = 'otp/verify.html'

    def get_context_data(self, **kwargs):
        context = super(VerifyView, self).get_context_data(**kwargs)
        context['form'] = SelectOTPDeviceForm(user=self.request.user)
        return context
