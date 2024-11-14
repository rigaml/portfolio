from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

from profits.models import Split
from profits.serializers import SplitSerializer


class TestSplitList(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('profits.views.Split.objects.all')
    def test_split_list_given_get_request_returns_splits(self, mock_split_all):
        """
        Tests get list splits
        """
        mock_split_1 = Split(
            id = 1,
            date = "2024-08-08",
            origin = 1,
            target= 10,
            created_at = "2024-08-08")

        mock_split_all.return_value = [mock_split_1]

        url = reverse('split_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        expected_data = SplitSerializer([mock_split_1], many=True).data
        self.assertEqual(response.json(), expected_data)
