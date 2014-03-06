# -*- coding: UTF-8 -*-
#
# Copyright 2014 Cole Maclean
"""Tornado forms: simple form validation. 

Form fields.
"""

import re
import decimal

import tornado.escape

from .requirements import *
from .utils import FormError

class BaseField(object):
    
    def __init__(self, **kwargs):
        self.reqs = []
        self.errors = []
        self.messages = {}
        messages = kwargs.pop('messages', None)
        if messages:
            self.messages.update(messages)
        self._kwargs = kwargs
        
        self._load_req('required', Required, pass_val=False)
        self._load_req('in_list', InList)
        self._load_req('not_in_list', NotInList)
        self._load_req('regex', Regex)
        
    def _load_req(self, key, class_name, pass_val=True):
        if self._kwargs.get(key):
            message = self.messages.get(key)
            if pass_val:
                req = class_name(self._kwargs[key], message=message)
            else:
                req = class_name(message=message)
            self.reqs.append(req)
            
    @property
    def valid(self):
        return bool(not self.errors)
    
    def to_python(self, val):
        return val
        
    def validate(self, val):
        for req in self.reqs:
            try:
                req.test(val)
            except FormError as e:
                self.errors.append(e)
        
class TextField(BaseField):
    
    def __init__(self, **kwargs):
        super(TextField, self).__init__(**kwargs)
        self._load_req('min_length', MinLength)
        self._load_req('max_length', MaxLength)
        
    def to_python(self, val):
        try:
            return tornado.escape.to_unicode(val)
        except UnicodeDecodeError as e:
            self.errors.append(FormError("Invalid encoding."))

class IntField(BaseField):
    
    def __init__(self, **kwargs):
        super(TextField, self).__init__(**kwargs)
        self._load_req('min_value', MinValue)
        self._load_req('max_value', MaxValue)
            
    def to_python(self, val):
        try:
            return int(val, base=10)
        except ValueError as e:
            self.errors.append(FormError("Invalid input."))

class DateField(BaseField):
    
    def to_python(self, val):
        try:
            return datetime.datetime.strptime(val, '%Y-%m-%d').date
        except ValueError as e:
            self.errors.append(FormError("Invalid input."))
            
class TimeField(BaseField):
    
    def to_python(self, val):
        formats = ('%I:%M:%S %p', '%I:%M %p', '%I %p', '%I%p', '%H:%M:%S', '%H:%M', '%H',)
        err = None
        for format in formats:
            try:
                time = datetime.datetime.strptime(val, format)
            except ValueError as e:
                err = e
            else:
                return time
        
        if err:
            self.errors.append(FormError("Invalid input."))

class DecimalField(IntField):
    
    def to_python(self, val):
        try:
            return decimal.Decimal(val)
        except ValueError:
            self.errors.append(FormError("Invalid input."))

class EmailField(TextField):
    
    EMAIL_VALIDATOR = re.compile(r"[^@]+@[^@]+\.[^@]+")
    
    def __init__(self, **kwargs):
        super(EmailField, self).__init__(**kwargs)
        message = self.messages.get('email')
        req = Regex(self.EMAIL_VALIDATOR, message=message)
        self.reqs.append(req)
