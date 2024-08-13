import django
from django.test import TestCase, Client
from django.urls import reverse


class TestGetTotalsView(TestCase):

    BROKER = 'ING'
    DATE_START = '2023-01-01'
    DATE_END = '2023-12-31'
    TOTAL = 10000

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_totals_given_valid_params_return_json(self):
        """
        """
        url = reverse('get_totals', kwargs={'broker': self.BROKER})
        querystring = {
            'date_start': self.DATE_START,
            'date_end': self.DATE_END,
        }

        response = self.client.get(url, querystring)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'date_start': self.DATE_START,
            'date_end': self.DATE_END,
            'broker': self.BROKER,
            'total': self.TOTAL
        })
