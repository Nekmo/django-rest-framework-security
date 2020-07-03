from django.contrib.sessions.backends.base import SessionBase
from django.contrib.sessions.models import Session
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from rest_framework_security.authentication.models import UserSession
from rest_framework_security.authentication.next_steps import get_next_steps, get_next_required_steps
from rest_framework_security.authentication.serializers import LoginSerializer, LogoutSerializer, UserSessionSerializer, \
    NextStepSerializer
from rest_framework_security.brute_force_protection.views import protect_api_request
from rest_framework_security.views import IsOwnerViewSetMixin
from django.utils.translation import gettext_lazy as _


class PostApiViewMixin:
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(PostApiViewMixin, GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = ()

    @protect_api_request(True)
    def post(self, request, *args, **kwargs):
        return super(LoginAPIView, self).post(request, *args, **kwargs)


class LogoutAPIView(PostApiViewMixin, GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)


class NextStepAPIView(ListAPIView):
    serializer_class = NextStepSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return list(filter(lambda next_step: next_step.is_required(self.request), get_next_steps()))


class UserSessionAPIView(IsOwnerViewSetMixin, viewsets.mixins.DestroyModelMixin, ReadOnlyModelViewSet):
    serializer_class = UserSessionSerializer
    permission_classes = (IsAuthenticated,)
    queryset = UserSession.objects.all()

    def get_serializer_class(self):
        if self.action == 'purge':
            return serializers.Serializer
        else:
            return super(UserSessionAPIView, self).get_serializer_class()

    @action(detail=False, methods=['POST'])
    def purge(self, request, *args, **kwargs):
        session: SessionBase = request.session
        queryset = self.filter_queryset(self.get_queryset()).exclude(session_key=session.session_key)
        count = queryset.clean_and_delete()[0]
        return Response({'detail': _('Removed {} sessions').format(count)})
