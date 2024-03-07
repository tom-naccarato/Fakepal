from django import template

register = template.Library()

CURRENCY_SYMBOLS = {
    'GBP': '£',
    'USD': '$',
    'EUR': '€',
}


@register.filter
def currency_symbol(value):
    """
    This function is used to get the currency symbol for the given currency code.
    :param value: Currency code
    :return:
    """
    return CURRENCY_SYMBOLS.get(value.upper(), value)
