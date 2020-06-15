from django.utils.module_loading import import_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from customers.permissions import IsOwner
from rest_framework_security.allowed_ips import config
from rest_framework_security.allowed_ips.serializers import UserIpSerializer, CreateUserIpSerializer, \
    UserIpConfigSerializer
from rest_framework_security.views import IsOwnerViewSetMixin
from rest_framework import filters


class UserIpViewSet(IsOwnerViewSetMixin, ModelViewSet):
    permission_classes = (
        IsOwner,
    )
    authentication_classes = (
    )
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    search_fields = (
        'ip_address', 'action'
    )
    serializer_class = UserIpSerializer
    ordering_fields = (
        'id', 'ip_address', 'action', 'last_used_at', 'created_at', 'updated_at',
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserIpSerializer
        else:
            return UserIpSerializer


class UserIpConfigViewSet(IsOwnerViewSetMixin, ModelViewSet):
    permission_classes = (
        IsOwner,
    )
    serializer_class = UserIpConfigSerializer

    def get_serializer_class(self):
        serializer_class = super(UserIpConfigViewSet, self).get_serializer_class()
        serializer_class.Meta.model = import_string(config.ALLOWED_IPS_USER_IP_CONFIG_MODEL)
        return serializer_class
