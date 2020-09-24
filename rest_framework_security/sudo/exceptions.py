# -*- coding: utf-8 -*-

"""Exceptions for djangorestframework-sudo."""
import sys


class RestFrameworkSudoError(Exception):
    body = ''

    def __init__(self, extra_body=''):
        self.extra_body = extra_body

    def __str__(self):
        msg = self.__class__.__name__
        if self.body:
            msg += ': {}'.format(self.body)
        if self.extra_body:
            msg += ('. {}' if self.body else ': {}').format(self.extra_body)
        return msg


def catch(fn):
    def wrap(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except RestFrameworkSudoError as e:
            sys.stderr.write('[Error] djangorestframework-sudo Exception:\n{}\n'.format(e))
    return wrap
