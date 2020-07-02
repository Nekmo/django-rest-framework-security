from django.contrib.auth import user_logged_in
from django.dispatch import receiver

from rest_framework_security.authentication.next_steps import get_next_steps


@receiver(user_logged_in)
def set_next_steps(sender, request, user, **kwargs):
    for next_step in get_next_steps():
        next_step.reset_state(request)
        next_step.update_state(request)
