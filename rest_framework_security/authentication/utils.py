from importlib import import_module
from typing import Type

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase


def get_session_store_class() -> Type[SessionBase]:
    return import_module(settings.SESSION_ENGINE).SessionStore
