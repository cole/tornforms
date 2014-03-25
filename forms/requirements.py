# -*- coding: UTF-8 -*-
#
# Copyright 2014 Cole Maclean
"""Tornado forms: simple form validation. 

Requirement validation.
"""

from forms.utils import FormError

class BaseRequirement(object):
    def __init__(self, *args, message=None):
        self.args = args
        if message is not None:
            self.message = message
            
    def __repr__(self):
        name = self.__class__.__name__.lower()
        if self.args:
            return '{0}: {1}'.format(name, self.args)
        else:
            return name
            
class Required(BaseRequirement):
    message = "This field is required."
    
    def test(self, val):
        if val in (None, '', [], {}):
            raise FormError(self.message, params={})
            
class MinLength(BaseRequirement):
    message = "{length} characters minimum, please."
        
    def test(self, val):
        if (not val) or (len(val) < self.args[0]):
            raise FormError(self.message, params={'length': self.args[0]})
            
class MaxLength(BaseRequirement):
    message = "{length} characters maximum, please."
    
    def test(self, val):
        if val and (len(val) > self.args[0]):
            raise FormError(self.message, params={'length': self.args[0]})
            
class MinValue(BaseRequirement):
    message = "This field must be at least {limit}."
    
    def test(self, val):
        if (not val) or (val < self.args[0]):
            raise FormError(self.message, params={'limit': self.args[0]})
            
class MaxValue(BaseRequirement):
    message = "This field must be less than {limit}."
    
    def test(self, val):
        if val and val > self.args[0]:
            raise FormError(self.message, params={'limit': self.args[0]})

class InList(BaseRequirement):
    message = "This field must be one of: {list}."
    
    def test(self, val):
        if val not in self.args[0]:
            raise FormError(self.message, params={'list': ", ".join(self.args[0])})
            
class NotInList(BaseRequirement):
    message = "This field must not be one of: {list}."
    
    def test(self, val):
        if val in self.args[0]:
            raise FormError(self.message, params={'list': ", ".join(self.args[0])})
            
class Regex(BaseRequirement):
    message = "This entry is invalid."
    
    def test(self, val):
        if not self.args[0].match(val):
            raise FormError(self.message, params={})