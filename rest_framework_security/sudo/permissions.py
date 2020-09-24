from rest_framework.permissions import BasePermission

from rest_framework_sudo.expiration import get_user_remaning_time


class Sudo(BasePermission):
    """
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(get_user_remaning_time(user))
