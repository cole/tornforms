# -*- coding: UTF-8 -*-
#
# Copyright 2014 Cole Maclean
"""Tornado forms: simple form validation. 

Utility classes.
"""

class FormError(Exception):
    
    def __init__(self, message, code=None, params=None):
        self.message = message
        self.params = params
        
    def __str__(self):
        if self.params:
            return self.message.format(**self.params)
        else:
            return self.message
