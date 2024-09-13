import django
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import MagicMock, patch

from profits.models import Broker, Currency, Operation
from profits.serializer import OperationSerializer


class TestOperationList(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('profits.views.Operation.objects.filter')
    @patch('profits.views.get_object_or_404')
    def test_operation_list_given_get_request_returns_operations(self, mock_get_object_or_404, mock_operation_filter):
        """
        Tests get list operations
        """

        mock_broker= Broker(id=2, name="ING", full_name="ING", created_at="2024-08-08")
        mock_get_object_or_404.return_value = mock_broker

        mock_operation_1 = Operation(
            id = 15,
            date = "2024-08-08",
            broker = mock_broker,
            type="BUY",
            ticker= "TSLA",
            exchange= "NASDAQ",
            quantity= 100,
            currency = Currency(id=3, iso_code="USD", description="USD", created_at="2024-08-08"),
            amount_total = 1234.23,
            created_at = "2024-08-08"
        )

        mock_queryset = MagicMock()
        mock_queryset.all.return_value = [mock_operation_1]

        mock_operation_filter.return_value = mock_queryset

        url = reverse('operation_list', kwargs={'broker_name': "ING"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        expected_data = OperationSerializer([mock_operation_1], many=True).data
        self.assertEqual(response.json(), expected_data)
