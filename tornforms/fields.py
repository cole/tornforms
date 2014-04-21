# -*- coding: UTF-8 -*-
#
# Copyright 2014 Cole Maclean
"""Tornado forms: simple form validation. 

Form fields.
"""

import re
import decimal

from tornforms.requirements import *
from tornforms.utils import FormError, ErrorList, decapitalize

class BaseField(object):
    """Abstract base class for form fields.
    """
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
        """Returns str."""
        # Tornado gives us lists
        if isinstance(val, list):
            val = val[-1]
        try:
            return val.decode('utf-8')
        except AttributeError as e:
            return val
            
    def to_dict(self):
        """Return field requirements as dict.
        """
        obj = dict()
        for req in self.reqs:
            name = decapitalize(req.__class__.__name__)
            obj[name] = req.to_dict()
        return obj
        
    def validate(self, val):
        """Check value against field requirements.
        """
        errors = ErrorList()
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
    """Text field handler.
    
    Keyword args:
    required - required field boolean
    in_list - check for value included in list
    not_in_list - check for value excluded from list
    regex - check for regex match
    min_length - check for minimum value length int
    max_length - check for maximum value length int
    messages - custom messages dict
    """
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
        """Returns None or str."""
        val = super(TextField, self).to_python(val)
        if not val:
            return None
        else:
            return val

class EmailField(TextField):
    """Email field handler.
    
    Text field handler that includes a basic regex check for email formatting.
    
    Keyword args:
    required - required field boolean
    in_list - check for value included in list
    not_in_list - check for value excluded from list
    regex - check for regex match
    min_length - check for minimum value length int
    max_length - check for maximum value length int
    messages - custom messages dict
    """
    EMAIL_VALIDATOR = re.compile(r"[^@]+@[^@]+\.[^@]+")
    
    def __init__(self, required=False, in_list=False, not_in_list=False, regex=False,
        min_length=False, max_length=False,messages={}):
        super(EmailField, self).__init__(required=required, in_list=in_list,
            not_in_list=not_in_list, regex=regex, min_length=False,
            max_length=False, messages=messages)
        req = Regex(self.EMAIL_VALIDATOR, message=messages.get('regex'))
        self.reqs.append(req)

class IntField(BaseField):
    """Int field handler.
    
    Keyword args:
    required - required field boolean
    in_list - check for value included in list
    not_in_list - check for value excluded from list
    regex - check for regex match
    min_value - check for minimum value int
    max_value - check for maximum value int
    messages - custom messages dict
    """
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
        """Returns int."""
        val = super(IntField, self).to_python(val)
        if val in ('', None):
            return None
        else:
            return int(val, base=10)

class DecimalField(IntField):
    """Decimal field handler.
    
    Keyword args:
    required - required field boolean
    in_list - check for value included in list
    not_in_list - check for value excluded from list
    regex - check for regex match
    min_value - check for minimum value int
    max_value - check for maximum value int
    messages - custom messages dict
    """
    
    def to_python(self, val):
        """Returns decimal."""
        val = super(DecimalField, self).to_python(val)
        if val in ('', None):
            return None
        else:
            return decimal.Decimal(val)

class DateField(BaseField):
    """Date field handler.
    
    Keyword args:
    required - required field boolean
    in_list - check for value included in list
    not_in_list - check for value excluded from list
    regex - check for regex match
    messages - custom messages dict
    """
    
    def to_python(self, val):
        """Returns date."""
        val = super(DateField, self).to_python(val)
        if val in ('', None):
            return None
        else:
            return datetime.datetime.strptime(val, '%Y-%m-%d').date
            
class TimeField(BaseField):
    """Time field handler.
    
    Keyword args:
    required - required field boolean
    in_list - check for value included in list
    not_in_list - check for value excluded from list
    regex - check for regex match
    messages - custom messages dict
    """
    
    def to_python(self, val):
        """Returns time."""
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
