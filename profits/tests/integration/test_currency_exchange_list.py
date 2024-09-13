import django
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

from profits.models import Currency, CurrencyExchange
from profits.serializer import CurrencyExchangeSerializer

class TestCurrencyExchangeList(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('profits.views.CurrencyExchange.objects.all')
    def test_currency_exchange_list_given_get_request_returns_currency_exchanges(self, mock_currency_exchange_all):
        """
        Tests get list currency exchanges.
        """
        mock_currency_1 = CurrencyExchange(
            id = 35,
            date = "2024-08-08",
            origin = Currency(id=3, iso_code="USD", description="USD", created_at="2024-08-08"),
            target = Currency(id=4, iso_code="GBP", description="GBP", created_at="2024-08-08"),
            rate = 0.75,
            created_at = "2024-08-08")

        mock_currency_exchange_all.return_value = [mock_currency_1]

        url = reverse('currency_exchange_list', kwargs={'origin': "USD", 'target': "GBP"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        expected_data = CurrencyExchangeSerializer([mock_currency_1], many=True).data
        self.assertEqual(response.json(), expected_data)
