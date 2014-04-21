import json

from tornforms.utils import FormError

class Form(object):
    """Unbound form object.
    Does not store data or errors, just fields.
    """
    errors, data = {}, {}
    
    def __init__(self, **fields):
        self.fields = fields
        
    def validations(self):
        obj = dict()
        for name, field in self.fields.items():
            obj[name] = field.to_dict()
        return obj
        
    def clean(self, raw_data):
        """
        Arguments:
        
        raw_data - dict or data accessor (e.g. `lambda k, d: dict().get(k, d)`)
        """
        cleaned_data = {}
        for name, field in self.fields.items():
            try:
                val = raw_data(name, None)
            except TypeError:
                val = raw_data.get(name, None)
            try:
                cleaned_data[name] = field.to_python(val)
            except Exception as e:
                pass
        
        return cleaned_data
        
    def validate(self, raw_data):
        """
        Arguments:
        
        raw_data - dict or data accessor (function, called with key)"""
        cleaned_data = self.clean(raw_data)
        errors = {}
        for name, field in self.fields.items():
            field_errors = field.validate(cleaned_data.get(name))
            if field_errors:
                errors[name] = field_errors
        
        return cleaned_data, errors

    def bind(self, handler, name='form'):
        """Create a new bound form as an attribute 
        on the RequestHandler.
        """
        bound_form = BoundForm(self, handler)
        setattr(handler, name, bound_form)

class BoundForm:
    def __init__(self, form, handler):
        self.unbound_form = form
        
        accessor = lambda k, d: handler.get_argument(k, default=d, strip=True)
        self.data, self.errors = self.unbound_form.validate(accessor)
        self.is_valid = not bool(self.errors)
        
        for field, field_errors in self.errors.items():
            for index, error in enumerate(field_errors):
                # Update in place
                translated = handler.locale.translate(error.message).format(**error.params)
                self.errors[field][index] = translated
        
    @property
    def fields(self):
        return self.unbound_form.fields
        
    def add_error(self, field, message, **context):
        error = FormError(message, params=context)
        if field in self.errors:
            self.errors[field].append(error)
        else:
            self.errors[field] = [error]
    
    def to_json(self):
        return json.dumps({
            'validations': self.unbound_form.validations(),
            'data': self.data,
            'errors': self.errors
        })