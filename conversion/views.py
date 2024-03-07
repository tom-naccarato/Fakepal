from django.http import HttpResponse, HttpResponseBadRequest


def conversion(request, currency1, currency2, amount_of_currency1):
    print("test")
    # Dictionary of exchange rates
    exchange_rates = {
        'USD': {'EUR': 0.85, 'GBP': 0.75},
        'EUR': {'USD': 1.18, 'GBP': 0.89},
        'GBP': {'USD': 1.33, 'EUR': 1.12}
    }

    # Check if the request method is GET
    if request.method == 'GET':
        try:
            currency1 = currency1.upper()
            currency2 = currency2.upper()
            amount_of_currency1 = float(amount_of_currency1)

            # Check if the currencies are supported
            if currency1 in exchange_rates and currency2 in exchange_rates[currency1]:
                # Calculate the conversion rate
                rate = exchange_rates[currency1][currency2]
                converted_currency1 = float(amount_of_currency1 * rate)
                # Return the conversion rate as an HTTP response
                return HttpResponse(converted_currency1)
            else:
                # Return an error if one or both of the currencies are not supported
                return HttpResponseBadRequest('One or both of the provided currencies are not supported')
        except KeyError:
            # Return an error if the request does not contain the required parameters
            return HttpResponseBadRequest('Invalid request parameters')
    else:
        # Return an error if the request method is not GET
        return HttpResponseBadRequest('Invalid request method')
