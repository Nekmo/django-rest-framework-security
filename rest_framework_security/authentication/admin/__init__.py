from django.contrib import admin
from rest_framework_security.authentication.models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    """
    list_display = (
        'id', 'user', 'ip_address', 'device', 'os', 'browser', 'session_expires', 'max_session_renewal',
        'created_at', 'updated_at',
    )
    list_display_links = ('id', 'user', 'ip_address', 'device', 'os', 'browser')
    search_fields = (
        'user__username', 'ip_address', 'user_agent',
    )
    autocomplete_fields = ('user',)
    fieldsets = (
        (None, {
            'fields': (
                'user', 'ip_address', 'user_agent',
                ('session_expires', 'max_session_renewal'),
                ('created_at', 'updated_at'),
            )
        }),
    )

    def delete_queryset(self, request, queryset):
        queryset.clean_and_delete()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
