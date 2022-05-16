from importlib import import_module

from django.conf import settings
from rest_framework.validators import ValidationError

PASSWORD_VALIDATORS = [
    getattr(import_module(m[0]), m[1])()
    for m in [
        dct["NAME"].rsplit(".", maxsplit=1) for dct in settings.AUTH_PASSWORD_VALIDATORS
    ]
]


def six_digits(value):
    if len(value) != 6 or not value.isdigit():
        raise ValidationError("The entered value is not 6 digits.")
