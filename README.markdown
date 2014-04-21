# tornforms

## Introduction

A basic form validation library for Tornado.

Forms are a collection of fields, passed to the Form class
constructor. Fields have optional requirements that must
all pass for the form to validate.

### Basic usage

Pass a series of Fields as keyword arguments to a `Form` object.

Calling validate on the object with form data (can be a dict,
`HTTPRequest.arguments`, or a callable that accepts a field_name
and default value arg) returns a tuple of cleaned data and errors (both dicts)

    foo_form = Form(test=TextField(required=True, min_length=10))
    
    form_data = { 
        'test': 'a_string'
    }
    
    clean, errors = foo_form.validate(form_data)
    # In a RequestHandler, we could also do
    # foo_form.validate(self.request.arguments)
    # or
    # foo_form.validate(lambda f, d: self.get_argument(f, default=d))
    
    # clean is: { 'test': 'a_string' }
    
    if errors:
        print(errors)
        # gives { 'test': "10 characters minimum, please."}
    else:
        print("A OK!")

### `with_form` Decorator

An easier way to use tornforms with Tornado is the `with_form` decorator.
    
    @with_form(foo_form)
    def post(self):
        if self.form.is_valid:
            # do something with self.form.data
        else:
            self.write(self.form.errors)
            
`@with_form` takes a `Form` object, and an optional name keyword argument.
It attaches a `BoundForm` object to the `RequestHandler` as the _name_ attribute ('form'
by default). The bound for object has four main attributes of interest:

* `is_valid`: boolean, true if all validations passed
* `data`: cleaned form data dict
* `errors`: form errors dict
* `fields`: form fields dict

## Field types

### All fields

All field types accept the following requirements as initialization
parameters:

 * required: raise error if value is not given.
 * in_list: raise error if value is not in the supplied list.
 * not_in_list: raise error if value is in the supplied list.
 * regex: raise error if value does not match regex.


Additionally, the `messages` parameter can be given, with a 
dict of strings to override the default error messages for each
requirement, e.g. `messages=dict(min_length="Not long enough!!!")`

### TextField

Cleans data to a string. The following additional requirements
are supported:

 * min_length: raise error if value is less than int chars.
 * max_length: raise error if value is more than int chars.

### EmailField

As `TextField`, but adds a regex check for basic address formatting.

### IntField

Cleans data to an int. In addition to the defaults, the following requirements
are supported:

 * min_value: raise error if value is less than int.
 * max_value: raise error if value is more than int.
 
### DecimalField

As `IntField`, but cleans to decimal.

### DateField

Cleans data to a date object.

### TimeField

Cleans data to a time object.
 
