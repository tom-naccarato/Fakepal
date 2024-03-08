import requests
from decimal import Decimal

from payapp.custom_exceptions import CurrencyConversionError


def convert_currency(currency1, currency2, amount_of_currency1):
    """
    Utility function to convert an amount of currency1 to currency2 using the currency conversion RESTful service
    :param currency1:
    :param currency2:
    :param amount_of_currency1:
    :return:
    """
    # If the currencies are the same, return the amount of currency1
    if currency1 == currency2:
        return amount_of_currency1
    try:
        response = requests.get(f'http://localhost:8000/webapps2024/conversion/{currency1.upper()}/{currency2.upper()}/'
                                f'{amount_of_currency1}')
    except Exception:
        raise CurrencyConversionError('Error in currency conversion, please try again')
    # If the request is unsuccessful, raise an exception
    if response.status_code != 200:
        raise CurrencyConversionError('Error in currency conversion, please try again')

    # If the request is successful, returns the result, which is the amount of currency1 converted to currency2
    converted_amount = Decimal(float(response.content))
    return converted_amount
