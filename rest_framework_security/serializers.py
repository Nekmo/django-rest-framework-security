from rest_framework import serializers


class SetUserMixin:
    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class GeoIPSerializerMixin(serializers.Serializer):
    city = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    continent = serializers.SerializerMethodField()
    postal = serializers.SerializerMethodField()
    subdivisions = serializers.SerializerMethodField()

    def get_city(self, obj):
        if obj.geoip2_city_record is None:
            return None
        language_code = self.context["request"].LANGUAGE_CODE
        return obj.geoip2_city_record.city.names.get(
            language_code, obj.geoip2_city_record.city.name
        )

    def get_country(self, obj):
        if obj.geoip2_city_record is None:
            return None
        language_code = self.context["request"].LANGUAGE_CODE
        return obj.geoip2_city_record.country.names.get(
            language_code, obj.geoip2_city_record.country.name
        )

    def get_continent(self, obj):
        if obj.geoip2_city_record is None:
            return None
        language_code = self.context["request"].LANGUAGE_CODE
        return obj.geoip2_city_record.continent.names.get(
            language_code, obj.geoip2_city_record.continent.name
        )

    def get_postal(self, obj):
        if obj.geoip2_city_record is None:
            return None
        return obj.geoip2_city_record.postal.code

    def get_subdivisions(self, obj):
        if obj.geoip2_city_record is None:
            return None
        language_code = self.context["request"].LANGUAGE_CODE
        return [
            subdivision.names.get(language_code, subdivision.name)
            for subdivision in obj.geoip2_city_record.subdivisions
        ]
