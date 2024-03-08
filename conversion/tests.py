from django.test import TestCase

from payapp.views import convert_currency


class TestConversion(TestCase):
    def test_100_gbp_to_usd_equals_133(self):
        """
        Test the conversion of 100 GBP to USD
        """
        self.assertEqual(convert_currency("GBP", "USD", 100), 133.0)

    def test_100_gbp_to_eur_equals_111(self):
        """
        Test the conversion of 100 GBP to EUR
        """
        self.assertEqual(convert_currency("GBP", "EUR", 100), 111.0)
