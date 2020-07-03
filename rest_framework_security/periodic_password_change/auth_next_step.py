from typing import Union

from django.shortcuts import redirect

from rest_framework_security.authentication.next_steps import get_admin_base_url, NextStepBase
from rest_framework_security.periodic_password_change.utils import password_is_expired
from django.utils.translation import gettext_lazy as _


class NextStep(NextStepBase):
    step_name = 'periodic_password_change'

    def get_allowed_urls(self):
        return [
            get_admin_base_url('password_change'),
            get_admin_base_url('password_change_done'),
        ]

    def get_admin_redirect(self):
        return redirect('admin:password_change')

    def is_required(self, request):
        return password_is_expired(request.user)

    def get_title(self):
        return _('Periodic Password Change')

    def get_description(self):
        return _(
            'It is mandatory to change the password before continuing. '
            'This security measure avoids using the same password for a '
            'long time.'
        )
