from logging import getLogger

from rest_framework.serializers import ModelSerializer

from rest_framework_security.allowed_ips.models import UserIp
from rest_framework_security.serializers import SetUserMixin, GeoIPSerializerMixin

logger = getLogger(__name__)


class CreateUserIpSerializer(SetUserMixin, ModelSerializer):
    class Meta:
        model = UserIp
        exclude = ("user",)
        read_only_fields = ("last_used_at",)


class UserIpSerializer(GeoIPSerializerMixin, CreateUserIpSerializer):
    class Meta(CreateUserIpSerializer.Meta):
        read_only_fields = CreateUserIpSerializer.Meta.read_only_fields + (
            "ip_address",
        )


class UserIpConfigSerializer(SetUserMixin, ModelSerializer):
    class Meta:
        model = None
        fields = ("default_ip_action",)
