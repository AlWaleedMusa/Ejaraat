from django import template
from babel.numbers import format_number
from core.models import RentProperty

register = template.Library()

@register.filter
def format_numbers(value):
    """
    """
    return format_number(value, locale="en_US")


@register.filter
def expected_income(rent_property, obj):
    """
    """
    return rent_property.expected_income(obj)