from typing import Union

from django.http import HttpRequest
from rest_framework.request import Request


def is_request(value):
    return isinstance(value, (Request, HttpRequest))


def get_request_argument(args=(), kwargs=None) -> Union[Request, HttpRequest, None]:
    for i in range(2):
        if i >= len(args):
            break
        value = args[i]
        if is_request(value):
            return value
    if "request" in kwargs and is_request(kwargs["request"]):
        return kwargs["request"]
    return None
