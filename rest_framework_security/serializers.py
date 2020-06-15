

class SetUserMixin:
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
