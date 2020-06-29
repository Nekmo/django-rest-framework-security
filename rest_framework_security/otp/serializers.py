from rest_framework import serializers

from rest_framework_security.otp.models import OTPDevice, get_engine


class OTPDeviceSerializer(serializers.ModelSerializer):
    data = serializers.JSONField(write_only=True)
    is_active = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = OTPDevice
        read_only_fields = ('last_use_at', 'counter', 'is_active')
        fields = (
            'url', 'id', 'title', 'otp_type', 'destination_type', 'destination_value', 'data',
            'counter', 'last_use_at', 'is_active', 'updated_at', 'created_at',
        )


class OTPDeviceCreateSerializer(OTPDeviceSerializer):
    def validate(self, attrs):
        request = self.context['request']
        validated_data = super(OTPDeviceSerializer, self).validate(attrs)
        validated_data['user'] = request.user
        validated_data = get_engine(validated_data['otp_type']).confirm_register(request, validated_data)
        return validated_data


class OTPDeviceBeginRegisterSerializer(OTPDeviceSerializer):
    class Meta(OTPDeviceSerializer.Meta):
        fields = ('otp_type', 'destination_type')
