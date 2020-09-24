from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_framework_sudo.expiration import get_user_remaning_time, get_expires_at, expire_now


class StatusSerializer(serializers.Serializer):
    remaning_time = serializers.DurationField()

    def get_initial(self):
        user = self.context['request'].user
        remaning_time = get_user_remaning_time(user)
        return {
            'remaning_time': remaning_time,
            'is_expired': not remaning_time,
        }


class UpdateStatusSerializer(serializers.Serializer):
    password = serializers.CharField()

    def validate_password(self, raw_password):
        user: AbstractUser = self.context['request'].user
        if not user.check_password(raw_password):
            raise ValidationError('Invalid password')

    def create(self, validated_data):
        user: AbstractUser = self.context['request'].user
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return {'password': ''}


class ExpireNowSerializer(serializers.Serializer):
    remaning_time = serializers.DurationField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        user: AbstractUser = self.context['request'].user
        expire_now(user)
        remaning_time = get_user_remaning_time(user)
        return {
            'remaning_time': remaning_time,
            'is_expired': not remaning_time,
        }
