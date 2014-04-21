# -*- coding: UTF-8 -*-
# Copyright 2014 Cole Maclean
"""Unit tests for form handling."""

import unittest
try:
    from urllib.parse import urlencode #py3
except ImportError:
    from urllib import urlencode #py2

import tornado.web
import tornado.testing

from tornforms import *
import tornforms.requirements

required_form =Form(test=TextField(required=True))

not_required_form =Form(test=TextField(required=False))

custom_msg_form =Form(test=TextField(required=True, messages={
        'required': "HI, we needs some data."
    }))

min_length_form =Form(test=TextField(min_length=6))

max_length_form =Form(test=TextField(max_length=3))

min_value_form =Form(test=IntField(min_value=7))

max_value_form =Form(test=IntField(max_value=168))

more_complex_form =Form(some_text=TextField(required=True),
    an_int=IntField(max_value=168))

unpythonic_field_names_form =Form(**{
    '-23432dsf-sd': TextField(required=True),
    '**dfswdfhe': IntField(max_value=168)
})

class FormTests(unittest.TestCase):    
    """Basic form handling tests.
    """ 
    def test_cleaned_data(self):
        encoded = u'Ümläüts'.encode('utf-8')
        
        cleaned_data, errors = required_form.validate({
            'test': encoded
        })
    
        self.assertEqual(len(errors), 0)
        self.assertNotEqual(cleaned_data['test'], encoded)
        self.assertEqual(cleaned_data['test'], u'Ümläüts')
        
    def test_bad_encoding(self):
        cleaned_data, errors = required_form.validate({
            'test': u'Ümläüts'.encode('latin-1')
        })
        
        self.assertEqual(len(errors), 1)
        
    def test_field_names_allowed(self):
        cleaned_data, errors = unpythonic_field_names_form.validate({
            '-23432dsf-sd': 'Hello World',
            '**dfswdfhe': 18
        })
        
        self.assertEqual(len(errors), 0)

class RequiredTests(unittest.TestCase):    
    """Test each requirement pass/fail.
    """
    def test_required_pass(self):
        cleaned_data, errors = required_form.validate({
            'test': 'The Quick Brown Fox',
        })
        self.assertEqual(len(errors), 0)
        
    def test_required_fail(self):
        cleaned_data, errors = required_form.validate({
            'test': ''
        })
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors['test'][0].message,
           tornforms.requirements.Required.message)

    def test_required_custom_message(self):
        cleaned_data, errors = custom_msg_form.validate({})
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors['test'][0].message, "HI, we needs some data.")

class MinMaxLengthTests(unittest.TestCase):    
    """Test each requirement pass/fail.
    """
    
    def test_basic_min_passes(self):
        cleaned_data, errors = min_length_form.validate({
            'test': 'Test Test Test Test'
        })
        self.assertEqual(len(errors), 0)
        
    def test_basic_min_fails(self):
        cleaned_data, errors = min_length_form.validate({
            'test': 'Test'
        })
        self.assertEqual(len(errors), 1)
        msg =tornforms.requirements.MinLength.message.format(length=6)
        self.assertEqual(str(errors['test'][0]), msg)

    def test_empty_min_fails(self):
        cleaned_data, errors = min_length_form.validate({
            'test': ''
        })
        self.assertEqual(len(errors), 1)
        msg =tornforms.requirements.MinLength.message.format(length=6)
        self.assertEqual(str(errors['test'][0]), msg)
        
    def test_basic_max_passes(self):
        cleaned_data, errors = max_length_form.validate({
            'test': 'ff'
        })
        self.assertEqual(len(errors), 0)
        
    def test_basic_max_fails(self):
        cleaned_data, errors = max_length_form.validate({
            'test': 'ffdddsds'
        })
        self.assertEqual(len(errors), 1)
        msg =tornforms.requirements.MaxLength.message.format(length=3)
        self.assertEqual(str(errors['test'][0]), msg)
        
    def test_empty_max_passes(self):
        cleaned_data, errors = max_length_form.validate({
            'test': ''
        })
        self.assertEqual(len(errors), 0)

class MinMaxValueTests(unittest.TestCase):    
    """Test each requirement pass/fail.
    """
    
    def test_basic_min_passes(self):
        cleaned_data, errors = min_value_form.validate({
            'test': '8'
        })
        self.assertEqual(len(errors), 0)
    
    def test_basic_min_fails(self):
        cleaned_data, errors = min_value_form.validate({
            'test': '6'
        })
        self.assertEqual(len(errors), 1)
        
    def test_empty_min_fails(self):
        cleaned_data, errors = min_value_form.validate({
            'test': ''
        })
        self.assertEqual(len(errors), 1)
        msg =tornforms.requirements.MinValue.message.format(limit=7)
        self.assertEqual(str(errors['test'][0]), msg)
        
    def test_basic_max_passes(self):
        cleaned_data, errors = max_value_form.validate({
            'test': '8'
        })
        self.assertEqual(len(errors), 0)
    
    def test_basic_max_fails(self):
        cleaned_data, errors = max_value_form.validate({
            'test': '655'
        })
        self.assertEqual(len(errors), 1)
        msg =tornforms.requirements.MaxValue.message.format(limit=168)
        self.assertEqual(str(errors['test'][0]), msg)
        
    def test_empty_max_passes(self):
        cleaned_data, errors = max_value_form.validate({
            'test': ''
        })
        self.assertEqual(len(errors), 0)

class FormWrapperHandler(tornado.web.RequestHandler):
    
    @with_form(more_complex_form)
    def post(self):
        if self.form.is_valid:
            self.write("OK!")
        else:
            self.write(', '.join(self.form.errors.keys()))
            
class NamedFormHandler(tornado.web.RequestHandler):
    
    @with_form(more_complex_form, name='foobar')
    def post(self):
        if self.foobar.is_valid:
            self.write("OK!")
        else:
            self.write(', '.join(self.foobar.errors.keys()))
            
class FormWrapperTests(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        settings = {
            'cookie_secret': "blahblahblahblahdfsdfds",
            'log_function': lambda s: s, # hide web server logs
        }
        return tornado.web.Application([
            (r"/form_post", FormWrapperHandler),
            (r"/named_post", NamedFormHandler),
        ], **settings)

    @tornado.testing.gen_test
    def test_form_handler_pass(self):
        data = {
            'some_text': 'The quick brown fox.',
            'an_int': 123
        }
        post = yield self.http_client.fetch(self.get_url('/form_post'),
            method="POST", body=urlencode(data))
        self.assertEqual(post.body.decode('utf-8'), "OK!")
        
    @tornado.testing.gen_test
    def test_form_handler_fail(self):
        data = {
            'some_text': '',
            'an_int': 999
        }
        post = yield self.http_client.fetch(self.get_url('/form_post'),
            method="POST", body=urlencode(data))
        error_fields = post.body.decode('utf-8').split(', ')
        self.assertTrue('some_text' in error_fields)
        self.assertTrue('an_int' in error_fields)
        
    @tornado.testing.gen_test
    def test_named_form_handler_pass(self):
        data = {
            'some_text': 'The quick brown fox.',
            'an_int': 123
        }
        post = yield self.http_client.fetch(self.get_url('/named_post'),
            method="POST", body=urlencode(data))
        self.assertEqual(post.body.decode('utf-8'), "OK!")

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(FormTests)
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(RequiredTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(MinMaxLengthTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(MinMaxValueTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(FormWrapperTests))
    
    return suite
    
if __name__ == '__main__':        
    all = lambda: suite()
    tornado.testing.main()

