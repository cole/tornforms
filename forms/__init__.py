# -*- coding: UTF-8 -*-
#
# Copyright 2014 Cole Maclean
"""Tornado forms: simple form validation. 
Forms are a collection of fields, passed to the Form class
constructor.
Fields have optional requirements that must all pass for
the form to validate.

    foo_form = Form({
        'test':  TextField(required=True, min_length=10)
    })
    
    clean, errors = foo_form.validate(self.request.arguments)
    if errors:
        self.write(foo_form.errors)
    else:
        clean # contains nice data
                
with the `with_form` wrapper:
    
    @with_form(FooForm)
    def post(self):
        if self.is_valid:
            ...
        else:
            self.write(self.errors)
"""
import functools

import tornado.web

from forms.fields import BaseField
from forms.utils import FormError

class Form(object):
    
    def __init__(self, fields, **kwargs):
        self.fields = fields
        self.fields.update(kwargs)
        
    def clean(self, raw_data):
        cleaned_data = {}
        for name, field in self.fields.items():
            val = raw_data.get(name, None)
            try:
                cleaned_data[name] = field.to_python(val)
            except Exception as e:
                pass
        
        return cleaned_data
        
    def validate(self, raw_data):
        cleaned_data = self.clean(raw_data)
        errors = {}
        for name, field in self.fields.items():
            field_errors = field.validate(cleaned_data.get(name))
            if field_errors:
                errors[name] = field_errors
        
        return cleaned_data, errors
        
def with_form(form=None):
    """Decorator for handler methods.
    Automatically sets up the form class given.
    """
    def decorator(method):
        assert form is not None, "Form instance required."
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            self.cleaned_data, self.errors = form.validate(self.request.arguments)
            self.is_valid = not bool(self.errors)
            return method(self, *args, **kwargs)
        return wrapper
    return decorator
