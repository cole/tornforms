# -*- coding: UTF-8 -*-
#
# Copyright 2014 Cole Maclean
"""Tornado forms: simple form validation. 

Requirement validation.
"""

from .utils import FormError

class BaseRequirement(object):
    def __init__(self, message=None):
        self.message = message or self.default_message
            
class Required(BaseRequirement):
    default_message = "This field is required."
    
    def test(self, val):
        if val in (None, '', [], {}):
            raise FormError(self.message, params={})
            
class MinLength(BaseRequirement):
    default_message = "{length} characters minimum, please."
    
    def __init__(self, length, **kwargs):
        super(MinLength, self).__init__(**kwargs)
        self.length = length
    
    def test(self, val):
        if len(val) < self.length:
            raise FormError(self.message, params={'length': self.length})
            
class MaxLength(MinLength):
    default_message = "{length} characters maximum, please."
    
    def test(self, val):
        if len(val) > self.length:
            raise FormError(self.message, params={'length': self.length})
            
class MinValue(BaseRequirement):
    default_message = "This field must be at least {limit}."
    
    def __init__(self, limit, **kwargs):
        super(MinValue, self).__init__(**kwargs)
        self.limit = limit
    
    def test(self, val):
        if val < self.limit:
            raise FormError(self.message, params={'limit': self.limit})
            
class MaxValue(MinValue):
    default_message = "This field must be less than {maximum}."
    
    def test(self, val):
        if val > self.limit:
            raise FormError(self.message, params={'limit': self.limit})

class InList(BaseRequirement):
    default_message = "This field must be one of: {list}."
    
    def __init__(self, list, **kwargs):
        super(InList, self).__init__(**kwargs)
        self.list = list
    
    @property
    def joined_list(self):
        return ", ".join(self.list)
    
    def test(self, val):
        if val not in self.list:
            raise FormError(self.message, params={'list': self.joined_list})
            
class NotInList(InList):
    default_message = "This field must not be one of: {list}."
    
    def test(self, val):
        if val in self.list:
            raise FormError(self.message, params={'list': self.joined_list})
            
class Regex(BaseRequirement):
    default_message = "This entry is invalid."
    
    def __init__(self, pattern, **kwargs):
        super(Regex, self).__init__(**kwargs)
        self.pattern = pattern
    
    def test(self, val):
        if not self.pattern.match(val):
            raise FormError(self.message, params={})