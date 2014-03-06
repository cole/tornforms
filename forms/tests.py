# -*- coding: UTF-8 -*-
# Copyright 2014 Cole Maclean
"""Unit tests for form handling."""

import unittest

import tornado.web
import tornado.testing

from forms import Form
from .fields import TextField, IntField
from .requirements import Required, MinLength, MaxLength

class MockHandler(tornado.web.RequestHandler):
    
    def __init__(self, data):
        self.data = data
        
    def get_argument(self, key, default=None, strip=True):
        return self.data.get(key, default)
        
class FormTests(unittest.TestCase):    
    """Basic form handling tests.
    """
    
    def setUp(self):
        try:
            encoded = 'Ümläüts'.encode('utf-8')
            encoded2 = 'Ümläüts'.encode('latin-1')
        except UnicodeDecodeError:
            # TODO: make python2 work
            encoded = 'Ümläüts'
            encoded2 = 'Ümläüts'
            
        self.data = {
            'test': 'The Quick Brown Fox',
            'empty': '',
            'bytes': encoded,
            'latin-1-sucks': encoded2
        }
        self.handler = MockHandler(self.data)
        
    def test_cleaned_data(self):
        form = Form(bytes=TextField(required=False))
        form.validate(self.data)
        
        encoded = 'Ümläüts'.encode('utf-8')
        
        self.assertEqual(len(form.errors), 0)
        self.assertNotEqual(form.cleaned_data['bytes'], encoded)
        self.assertEqual(form.cleaned_data['bytes'], 'Ümläüts')
        
    def test_bad_encoding(self):
        form = Form(**{
            'latin-1-sucks': TextField(required=False)
        })
        form.validate(self.data)
        self.assertEqual(len(form.errors), 1)

    def test_mock_handler(self):
        form = Form(test=TextField(required=True))
        form.validate(self.handler)
        self.assertEqual(len(form.errors), 0)

class RequiredTests(unittest.TestCase):    
    """Test each requirement pass/fail.
    """
    
    def setUp(self):
        self.data = {
            'test': 'The Quick Brown Fox',
            'empty': ''
        }
        self.handler = MockHandler(self.data)
    
    def test_required_pass(self):
        form = Form(test=TextField(required=True))
        form.validate(self.data)
        self.assertEqual(len(form.errors), 0)
        
    def test_required_fail(self):
        form = Form(empty=TextField(required=True))
        form.validate(self.data)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['empty'][0].message, Required.default_message)

    def test_required_custom_message(self):
        msg = "HI, we needs some data."
        form = Form(empty=TextField(required=True,
            messages={ 'required': msg}))
        form.validate(self.data)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['empty'][0].message, msg)

class MinMaxLengthTests(unittest.TestCase):    
    """Test each requirement pass/fail.
    """
    
    def setUp(self):
        self.data = {
            'test': 'Test Test Test Test',
            'test2': 'f',
            'test3': ''
        }
        self.handler = MockHandler(self.data)
    
    def test_basic_min_passes(self):
        form = Form(test=TextField(min_length=6))
        form.validate(self.data)
        self.assertEqual(len(form.errors), 0)
        
    def test_basic_min_fails(self):
        form = Form(test2=TextField(min_length=6))
        form.validate(self.data)
        self.assertEqual(len(form.errors), 1)
        msg = MinLength.default_message.format(length=6)
        self.assertEqual(form.errors['test2'][0].message, msg)

    def test_empty_min_fails(self):
        form = Form(test3=TextField(min_length=3))
        form.validate(self.data)
        self.assertEqual(len(form.errors), 1)
        msg = MinLength.default_message.format(length=3)
        self.assertEqual(str(form.errors['test3'][0]), msg)
        
    def test_basic_max_passes(self):
        form = Form(test2=TextField(max_length=3))
        form.validate(self.data)
        self.assertEqual(len(form.errors), 0)
        
    def test_basic_min_fails(self):
        form = Form(test=TextField(max_length=6))
        form.validate(self.data)
        self.assertEqual(len(form.errors), 1)
        msg = MaxLength.default_message.format(length=6)
        self.assertEqual(str(form.errors['test'][0]), msg)
        
    def test_empty_max_passes(self):
        form = Form(test3=TextField(max_length=3))
        form.validate(self.data)
        self.assertEqual(len(form.errors), 0)

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(FormTests)
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(RequiredTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(MinMaxLengthTests))
    return suite
    
if __name__ == '__main__':        
    all = lambda: suite()
    tornado.testing.main()

