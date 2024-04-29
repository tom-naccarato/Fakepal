from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ConversionSerializer


class ConversionAPI(APIView):
    """
    API to convert an amount of one currency to another currency

    The API expects the following parameters in the URL:
    - from_currency: The currency to convert from
    - to_currency: The currency to convert to
    - amount: The amount to convert

    The API returns the converted amount in the 'converted_amount' field of the response
    """
    def get(self, request, from_currency, to_currency, amount):
        # Data preparation for serialization
        try:
            amount = float(amount)  # Convert amount to float
        except ValueError:
            return Response({'error': 'Invalid amount format'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': amount
        }

        # If currencies are the same, return the amount
        if from_currency == to_currency:
            return Response({'converted_amount': amount})

        # Validation through serializer
        serializer = ConversionSerializer(data=data)
        if serializer.is_valid():
            valid_data = serializer.validated_data
            from_currency = valid_data['from_currency'].upper()
            to_currency = valid_data['to_currency'].upper()
            amount = valid_data['amount']

            # Dictionary of exchange rates
            exchange_rates = {
                'USD': {'EUR': 0.85, 'GBP': 0.75},
                'EUR': {'USD': 1.18, 'GBP': 0.89},
                'GBP': {'USD': 1.33, 'EUR': 1.12}
            }

            if from_currency in exchange_rates and to_currency in exchange_rates[from_currency]:
                rate = exchange_rates[from_currency][to_currency]
                converted_amount = round(amount * rate, 2)
                return Response({'converted_amount': converted_amount})
            else:
                return Response({'error': 'Unsupported currency'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)