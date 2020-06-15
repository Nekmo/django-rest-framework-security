from django.contrib import admin
from rest_framework_security.allowed_ips.models import UserIp


@admin.register(UserIp)
class UserIpAdmin(admin.ModelAdmin):
    """
    """
    list_display = (
        'id', 'user', 'ip_address', 'action', 'last_used_at', 'created_at', 'updated_at',
    )
    list_display_links = ('id', 'user', 'ip_address')
    list_filter = ('action',)
    search_fields = (
        'user', 'ip_address',
    )
    autocomplete_fields = ('user',)
    fieldsets = (
        (None, {
            'fields': (
                'user', 'ip_address', 'action',
            )
        }),
    )
