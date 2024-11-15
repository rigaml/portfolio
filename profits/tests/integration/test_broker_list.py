from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

from profits.models import Broker
from profits.serializers import BrokerSerializer


class TestBrokerList(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('profits.views.Broker.objects.all')
    def test_broker_list_given_get_request_returns_brokers(self, mock_broker_all):
        """
        Tests get list brokers
        """
        mock_broker_1 = Broker(
            id = 2,
            name = "ING",
            full_name = "ING",
            created_at = "2024-08-08")

        mock_broker_all.return_value = [mock_broker_1]

        url = reverse('broker_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        expected_data = BrokerSerializer([mock_broker_1], many=True).data
        self.assertEqual(response.json(), expected_data)
