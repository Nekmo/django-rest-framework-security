

class EngineBase:
    def begin_register(self, request):
        raise NotImplementedError

    def confirm_register(self, request, validated_data):
        raise NotImplementedError

    def challenge(self, request, otp_device):
        raise NotImplementedError

    def verify(self, request, otp_device, data):
        raise NotImplementedError

