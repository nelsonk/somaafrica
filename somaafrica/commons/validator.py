import phonenumbers

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validate_phone_number(value):
    try:
        # Parse the phone number with an optional region
        phone_number = phonenumbers.parse(value, None)

        # Validate the number
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError(f'{value} not a valid international number')

    except phonenumbers.NumberParseException:
        raise ValidationError(f'{value} is not a valid phone number format.')


def validate_email_address(value):
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False


def validate_email_return_filters(value):
    '''
    Validate email and return filters to be used to search user
    '''
    email_validated = validate_email_address(value)

    if email_validated:
        filters = {"email": value}
    else:
        filters = {"username": value}

    return filters
