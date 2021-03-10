from typing import Iterator, Union

from django.apps import apps
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.utils.module_loading import import_string

from rest_framework_security.periodic_password_change.utils import password_is_expired

NEXT_STEP_APPS = [
    "rest_framework_security.periodic_password_change",
    "rest_framework_security.otp",
]


class NextStepBase:
    step_name = None

    def get_allowed_urls(self):
        return []

    def get_admin_redirect(self):
        pass

    def is_active(self, request) -> Union[bool, None]:
        return request.session.get(self.step_name, None)

    def is_required(self, request):
        raise NotImplementedError

    def set_state(self, request, state):
        request.session[self.step_name] = state

    def reset_state(self, request):
        request.session.pop(self.step_name, None)

    def update_state(self, request):
        self.set_state(request, self.is_required(request))

    @property
    def title(self):
        return self.get_title()

    def get_title(self):
        return ""

    @property
    def description(self):
        return self.get_description()

    def get_description(self):
        return ""


def get_next_steps() -> Iterator[NextStepBase]:
    next_step_apps = filter(apps.is_installed, NEXT_STEP_APPS)
    next_steps = map(
        lambda x: import_string(f"{x}.auth_next_step.NextStep"), next_step_apps
    )
    yield from map(lambda next_step: next_step(), next_steps)


def get_next_required_steps(request) -> Iterator[str]:
    yield from filter(
        bool,
        map(
            lambda next_step: next_step.step_name
            if next_step.is_required(request)
            else None,
            get_next_steps(),
        ),
    )


def get_admin_base_url(name="index"):
    try:
        return reverse(f"admin:{name}")
    except NoReverseMatch:
        return
