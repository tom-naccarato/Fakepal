import decimal

import requests
from decimal import Decimal

from payapp.custom_exceptions import CurrencyConversionError


def convert_currency(currency1, currency2, amount_of_currency1):
    """
    Utility function to convert an amount of currency1 to currency2 using the currency conversion RESTful service.
    :param currency1: The currency to convert from.
    :param currency2: The currency to convert to.
    :param amount_of_currency1: The amount of currency1 to convert.
    :return: Decimal - The amount of currency2 after conversion.
    """
    # Makes sure that the input is uppercase
    currency1 = currency1.upper()
    currency2 = currency2.upper()
    # If the currencies are the same, return the amount as a Decimal
    if currency1 == currency2:
        return Decimal(amount_of_currency1)

    # Build the URL for the RESTful service
    url = f'http://localhost:8000/webapps2024/conversion/{currency1.upper()}/{currency2.upper()}/{amount_of_currency1}/'
    # Make a request to the RESTful service
    try:
        response = requests.get(url)

    # If there is a connection error, raise an exception
    except requests.exceptions.ConnectionError:
        print('Connection error, please check your network')
        raise CurrencyConversionError('Connection error, please check your network')
    # If there is a request exception, raise an exception
    except requests.exceptions.RequestException:
        print('Error in currency conversion, please try again')
        raise CurrencyConversionError('Error in currency conversion, please try again')

    # If the request is unsuccessful, raise an exception
    if response.status_code != 200:
        print('Error in currency conversion, response status: ' + str(response.status_code))
        raise CurrencyConversionError('Error in currency conversion, response status: ' + str(response.status_code))

    try:
        # Parsing JSON from the response and converting the specified field to Decimal
        data = response.json()
        converted_amount = Decimal(str(data['converted_amount']))  # Convert to string to avoid float precision issues
        print(converted_amount)
    except (ValueError, KeyError, decimal.InvalidOperation):
        print('Invalid response format from currency conversion service')
        raise CurrencyConversionError('Invalid response format from currency conversion service')

    return converted_amount
