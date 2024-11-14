from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock

from profits.models import Currency
from profits.serializers import CurrencySerializer


class TestCurrencyList(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('profits.views.Currency.objects.all')
    def test_currency_list_given_get_request_returns_currencies(self, mock_currency_all):
        """
        Tests get list currencies
        """
        mock_currency_1 = Currency(
            id = 3,
            iso_code = "USD",
            description = "USD",
            created_at = "2024-08-08")

        mock_currency_all.return_value = [mock_currency_1]

        url = reverse('currency_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        expected_data = CurrencySerializer([mock_currency_1], many=True).data
        self.assertEqual(response.json(), expected_data)
