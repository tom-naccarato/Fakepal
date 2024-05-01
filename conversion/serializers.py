from rest_framework import serializers


class ConversionSerializer(serializers.Serializer):
    """
    This class is used to validate the request data for the conversion API

    :param serializers:
    """
    # Define the fields that are expected in the request for validation
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    amount = serializers.FloatField(min_value=0)
