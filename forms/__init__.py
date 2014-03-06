# -*- coding: UTF-8 -*-
#
# Copyright 2014 Cole Maclean
"""Tornado forms: simple form validation. 
Should also work with json objects, dicts, etc.    

    foo_form = Form(test=TextField(required=True, min_length=10))
    foo_form.validate(self) # in a RequestHandler
    if foo_form.errors:
        self.write(errors)
    else:
        ...
"""

import tornado.web

class Form(object):
    
    def __init__(self, **fields):
        self.fields = {}
        self.fields.update(fields)
        self.errors = {}
        self.cleaned_data = {}
    
    def __getitem__(self, key):
        return self.fields[key]
    
    def clean(self, handler):
        if isinstance(handler, tornado.web.RequestHandler):
            getter = lambda k: handler.get_argument(k, default=None, strip=True)
        else:
            getter = lambda k: handler.get(k, None)
            
        for name, field in self.fields.items():
            val = getter(name)
            clean = field.to_python(val)
            self.cleaned_data[name] = clean
            
    def validate(self, handler):
        if not self.cleaned_data:
            self.clean(handler)
        for name, field in self.fields.items():
            field.validate(self.cleaned_data[name])
            if field.errors:
                self.errors[name] = field.errors
                    

