import phonenumbers
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    try:
        # Parse the phone number with an optional region
        phone_number = phonenumbers.parse(value, None)

        # Validate the number
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError(f'{value} not a valid international number')

    except phonenumbers.NumberParseException:
        raise ValidationError(f'{value} is not a valid phone number format.')
