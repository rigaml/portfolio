from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock

from profits.models import Currency, Dividend
from profits.serializers import DividendSerializer


class TestDividendList(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('profits.views.Dividend.objects.all')
    def test_dividend_list_given_get_request_returns_dividends(self, mock_dividend_all):
        """
        Tests get list dividend
        """
        mock_dividend_1 = Dividend(
            id = 4,
            date = "2024-08-08",
            ticker = "DNA",
            currency = Currency(iso_code="USD", description="USD", created_at="2024-08-08"),
            amount_total = 1234.23,
            created_at = "2024-08-08")

        mock_dividend_all.return_value = [mock_dividend_1]

        url = reverse('dividend_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        expected_data = DividendSerializer([mock_dividend_1], many=True).data
        self.assertEqual(response.json(), expected_data)
