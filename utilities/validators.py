from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def not_zero_validator(value):
    if value == 0:
        raise ValidationError("değer sıfır olamaz.")
