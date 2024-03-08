from django.http import HttpResponse, HttpResponseBadRequest


def conversion(request, currency1, currency2, amount_of_currency1):
    """
    RESTful Service for currency conversion.
    :param request: HTTP request
    :param currency1: The currency to convert from
    :param currency2: The currency to convert to
    :param amount_of_currency1: The amount of currency1 to convert
    :return: The amount of currency2 after conversion"""
    # Dictionary of exchange rates
    exchange_rates = {
        'USD': {'EUR': 0.85, 'GBP': 0.75},
        'EUR': {'USD': 1.18, 'GBP': 0.89},
        'GBP': {'USD': 1.33, 'EUR': 1.12}
    }

    # Check if the request method is GET
    if request.method == 'GET':
        if amount_of_currency1 == '0':
            return HttpResponse(amount_of_currency1)
        try:
            if float(amount_of_currency1) < 0:
                return HttpResponse('Cannot use negative amount of currency1', status=400)
            currency1 = currency1.upper()
            currency2 = currency2.upper()
            amount_of_currency1 = float(amount_of_currency1)

            # Check if the currencies are supported
            if currency1 in exchange_rates and currency2 in exchange_rates[currency1]:
                # Calculate the conversion rate
                rate = exchange_rates[currency1][currency2]
                converted_currency1 = round(float(amount_of_currency1 * rate), 2)
                # Return the conversion rate as an HTTP response
                return HttpResponse(converted_currency1)
            else:
                # Return an error if one or both of the currencies are not supported
                return HttpResponse('One or both of the provided currencies are not supported', status=400)
        except KeyError:
            # Return an error if the request does not contain the required parameters
            return HttpResponse('Invalid request parameters', status=400)
        except ValueError:
            # Return an error if the amount of currency1 is not a valid number
            return HttpResponse('Invalid amount of currency1', status=400)
    else:
        # Return an error if the request method is not GET
        return HttpResponse('Invalid request method', status=400)
