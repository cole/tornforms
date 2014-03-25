# -*- coding: UTF-8 -*-
#
# Copyright 2014 Cole Maclean
"""Tornado forms: simple form validation. 

Form fields.
"""

import re
import decimal

import tornado.escape

from forms.requirements import *
from forms.utils import FormError

class BaseField(object):
    
    def __init__(self, required=False, in_list=False, not_in_list=False, regex=False, messages={}):
        self.reqs = []
        
        if required:
            req = Required(message=messages.get('required'))
            self.reqs.append(req)
            
        if in_list:
            req = InList(in_list, message=messages.get('in_list'))
            self.reqs.append(req)
            
        if not_in_list:
            req = NotInList(not_in_list, message=messages.get('not_in_list'))
            self.reqs.append(req)
            
        if regex:
            req = Regex(regex, message=messages.get('regex'))
            self.reqs.append(req)
    
    def to_python(self, val):
        # Tornado gives us lists
        if isinstance(val, list):
            val = val[-1]
            
        try:
            return val.decode('utf-8')
        except AttributeError as e:
            return val
        
    def validate(self, val):
        errors = []
        for req in self.reqs:
            try:
                req.test(val)
            except FormError as e:
                errors.append(e)
        return errors
                
    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, 
            ' '.join([repr(req) for req in self.reqs]))
        
class TextField(BaseField):
    
    def __init__(self, required=False, in_list=False, not_in_list=False, regex=False,
        min_length=False, max_length=False, messages={}):
        super(TextField, self).__init__(required=required, in_list=in_list,
            not_in_list=not_in_list, regex=regex, messages=messages)
        
        if min_length:
            req = MinLength(min_length, message=messages.get('min_length'))
            self.reqs.append(req)
            
        if max_length:
            req = MaxLength(max_length, message=messages.get('max_length'))
            self.reqs.append(req)
        
    def to_python(self, val):
        val = super(TextField, self).to_python(val)
        if not val:
            return None
        else:
            return val
            
class IntField(BaseField):
    
    def __init__(self, required=False, in_list=False, not_in_list=False, regex=False,
        min_value=False, max_value=False, messages={}):
        super(IntField, self).__init__(required=required, in_list=in_list,
            not_in_list=not_in_list, regex=regex, messages=messages)
        
        if min_value:
            req = MinValue(min_value, message=messages.get('min_value'))
            self.reqs.append(req)
            
        if max_value:
            req = MaxValue(max_value, message=messages.get('max_value'))
            self.reqs.append(req)
            
    def to_python(self, val):
        val = super(IntField, self).to_python(val)
        if val in ('', None):
            return None
        else:
            return int(val, base=10)

class DateField(BaseField):
    
    def to_python(self, val):
        val = super(DateField, self).to_python(val)
        if val in ('', None):
            return None
        else:
            return datetime.datetime.strptime(val, '%Y-%m-%d').date
            
class TimeField(BaseField):
    
    def to_python(self, val):
        val = super(TimeField, self).to_python(val)
        if val in ('', None):
            return None
        else:
            formats = ('%I:%M:%S %p', '%I:%M %p', '%I %p', '%I%p', '%H:%M:%S', '%H:%M', '%H',)
            err = None
            for format in formats:
                try:
                    time = datetime.datetime.strptime(val, format)
                except ValueError as e:
                    err = e
                else:
                    return time
        
            return err

class DecimalField(IntField):
    
    def to_python(self, val):
        val = super(DecimalField, self).to_python(val)
        if val in ('', None):
            return None
        else:
            return decimal.Decimal(val)

class EmailField(TextField):
    
    EMAIL_VALIDATOR = re.compile(r"[^@]+@[^@]+\.[^@]+")
    
    def __init__(self, required=False, in_list=False, not_in_list=False, regex=False, messages={}):
        super(EmailField, self).__init__(required=required, in_list=in_list,
            not_in_list=not_in_list, regex=regex, messages=messages)
        req = Regex(self.EMAIL_VALIDATOR, message=messages.get('email'))
        self.reqs.append(req)
