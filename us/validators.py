import formencode
from formencode import validators

from us.models import User


class UniqueEmail(formencode.FancyValidator):
    
    def validate_python(self, value, state):
        if value in User.get_all_emails():
            raise formencode.Invalid(
                    'Email already exists',
                    value, state)
        return value


class Registration(formencode.Schema):
    email = formencode.All(validators.Email(resolve_domain=False, trim=True),
                           UniqueEmail())
    password = validators.String(min=6)
    password_confirm = validators.String(min=6)
    chained_validators = [validators.FieldsMatch('password', 
            'password_confirm')]
