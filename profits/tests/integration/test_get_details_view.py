import django
from django.test import TestCase, Client
from django.urls import reverse


class TestGetDetailsView(TestCase):

    BROKER = 'ING'
    DATE_START = '2023-01-01'
    DATE_END = '2023-12-31'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_details_given_valid_params_return_json(self):
        url = reverse('get_details', kwargs={'broker': self.BROKER})
        querystring = {
            'date_start': self.DATE_START,
            'date_end': self.DATE_END,
        }

        response = self.client.get(url, querystring)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'],
                         f'attachment; filename="{self.DATE_START}-{self.DATE_END}-{self.BROKER}-profits-details.csv"')
