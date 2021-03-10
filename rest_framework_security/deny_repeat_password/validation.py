from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class DenyRepeatPasswordValidator:
    def __init__(self):
        pass

    def validate(self, password, user=None):
        from rest_framework_security.deny_repeat_password.models import UserPassword

        if UserPassword.objects.filter(user=user).password_exists(password):
            raise ValidationError(
                _("The new password has been used previously."),
                code="deny_repeat_password",
            )

    def get_help_text(self):
        return _("Your password must not have been previously used by your user.")
