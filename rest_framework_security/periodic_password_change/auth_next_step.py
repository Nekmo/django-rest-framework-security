from rest_framework_security.periodic_password_change.utils import password_is_expired


def next_step_required(user):
    if password_is_expired(user):
        return 'change_password'
