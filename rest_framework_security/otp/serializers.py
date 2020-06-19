from rest_framework import serializers

from rest_framework_security.otp.models import OTPDevice


class OTPDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = OTPDevice
        fields = (
            'url', 'id', 'title', 'otp_type', 'destination_type', 'obfuscated_destination_value',
            'last_use_at', 'is_active', 'updated_at', 'created_at',
        )
