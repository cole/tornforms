# -*- coding: UTF-8 -*-
#
# Copyright 2014 Cole Maclean
"""Tornado forms: simple form validation. 

Utility classes.
"""
import functools

def decapitalize(string):
    """Turn MinLength into minLength for JS"""
    if not string:
        return string
    return "{0}{1}".format(string[:1].lower(), string[1:])

class ErrorList(list):
    """List of form errors
    On __str__, returns the first item.
    """
    def __str__(self):
        try:
            return str(self[0])
        except IndexError:
            return ''

class FormError(Exception):
    """Form validation error.
    """
    def __init__(self, message, code=None, params=None):
        self.message = message
        self.params = params
        
    def __str__(self):
        if self.params:
            return self.message.format(**self.params)
        else:
            return self.message

def with_form(form=None, name='form'):
    """Decorator for `tornado.web.RequestHandler` methods.
    Automatically sets up the form class given as  `self._name_`
    """
    def decorator(method):
        assert form is not None, "Form instance required."
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            form.bind(self, name=name)
            return method(self, *args, **kwargs)
        return wrapper
    return decorator