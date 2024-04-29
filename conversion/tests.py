from django.test import TestCase, Client
from django.urls import reverse
import json

class TestConversion(TestCase):
    def setUp(self):
        self.client = Client()

    def test_100_gbp_to_usd_equals_133(self):
        """
        Test the conversion of 100 GBP to USD
        """
        url = reverse('conversion:conversion', args=['GBP', 'USD', 100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['converted_amount'], 133.0)

    def test_100_gbp_to_eur_equals_112(self):
        """
        Test the conversion of 100 GBP to EUR
        """
        url = reverse('conversion:conversion', args=['GBP', 'EUR', 100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['converted_amount'], 112.0)

    def test_100_usd_to_gbp_equals_75(self):
        """
        Test the conversion of 100 USD to GBP
        """
        url = reverse('conversion:conversion', args=['USD', 'GBP', 100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['converted_amount'], 75.0)

    def test_4_20_usd_to_eur_equals_3_57(self):
        """
        Test the conversion of 4.20 USD to EUR
        """
        url = reverse('conversion:conversion', args=['USD', 'EUR', 4.20])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['converted_amount'], 3.57)

    def test_invalid_currency(self):
        """
        Test the conversion of an invalid currency
        """
        url = reverse('conversion:conversion', args=['GBP', 'INV', 100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), '{"error":"Unsupported currency"}')

    def test_invalid_request(self):
        """
        Test an invalid request
        """
        url = reverse('conversion:conversion', args=['GBP', 'USD', 'invalid'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), '{"error":"Invalid amount format"}')

    def test_large_amount(self):
        """
        Test a large amount of currency
        """
        url = reverse('conversion:conversion', args=['GBP', 'USD', 100000000000000000000])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['converted_amount'], 133000000000000000000.0)

    def test_negative_amount(self):
        """
        Test a negative amount of currency
        """
        url = reverse('conversion:conversion', args=['GBP', 'USD', -100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), '{"amount":["Ensure this value is greater than or equal to 0."]}')

    def test_unsupported_method(self):
        """
        Test an unsupported HTTP method (POST)
        """
        url = reverse('conversion:conversion', args=['GBP', 'USD', 100])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode(), '{"detail":"Method \\"POST\\" not allowed."}')
