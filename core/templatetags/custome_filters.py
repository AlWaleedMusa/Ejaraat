from django import template

from babel.numbers import format_number


register = template.Library()


@register.filter
def format_numbers(value):
    """
    Format a number using the Babel library.

    This filter formats a number using the Babel library and returns the formatted number.

    Args:
        value (int): The number to be formatted.

    Returns:
        str: The formatted number.
    """

    return format_number(value, locale="en_US")
