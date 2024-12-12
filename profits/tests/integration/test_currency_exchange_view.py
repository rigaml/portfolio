import pytest

import io
import csv
from datetime import timedelta

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from profits.models import CurrencyExchange

NON_EXISTING_ID = 999999

@pytest.fixture
def exchanges_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'ExchangeRate'])
    writer.writerow(['01 Jan 23', '1.15'])
    writer.writerow(['02 Jan 23', '1.16'])
    
    return SimpleUploadedFile(
        'exchange_rates.csv',
        output.getvalue().encode('utf-8'),
        content_type='text/csv'
    )

@pytest.mark.django_db
class TestCurrencyExchangeViewSet:

    def test_list_currency_exchange_when_no_currency_exchange_returns_empty_list(self, authenticated_client):
        url = reverse('currencyexchange-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_currency_exchange_when_single_currency_exchange_returns_one(self, authenticated_client, currency_exchange_default):
        url = reverse('currencyexchange-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_currency_exchange_when_multiple_currency_exchanges_returns_all(
            self, 
            authenticated_client, 
            create_currency_exchange,
            date_factory):
        create_currency_exchange()
        create_currency_exchange(date=date_factory('2024-02-01'))

        url = reverse('currencyexchange-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_currency_exchange_when_id_exists_returns_record(self, authenticated_client, currency_exchange_default):
        url = reverse('currencyexchange-detail', args=[currency_exchange_default.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == currency_exchange_default.date.date().isoformat()
        assert response.data['origin'] == currency_exchange_default.origin.iso_code
        assert response.data['target'] == currency_exchange_default.target.iso_code
        assert response.data['rate'] == f"{currency_exchange_default.rate:.6f}"

    def test_retrieve_currency_exchange_when_id_does_not_exist_returns_404(self, authenticated_client, currency_exchange_default):
        url = reverse('currencyexchange-detail', args=[NON_EXISTING_ID])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_currency_exchanges_success_returns_201(
            self, 
            authenticated_client, 
            currency_usd, 
            currency_eur, 
            exchanges_csv):
        
        url = reverse('currencyexchange-upload')
        data = {
            'origin': currency_usd.iso_code,
            'target': currency_eur.iso_code,
            'file': exchanges_csv
        }
        
        response = authenticated_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Successfully imported 2 exchange rates'
        assert CurrencyExchange.objects.count() == 2

    @pytest.mark.parametrize("missing_field",
                            [("origin"),
                              ("target"),
                              ("file")
                            ])
    def test_upload_currency_exchanges_when_missing_fields_returns_400(
        self, 
        authenticated_client, 
        currency_usd, 
        currency_eur, 
        exchanges_csv, 
        missing_field):

        url = reverse('currencyexchange-upload')
        data = {
            'origin': currency_usd.iso_code,
            'target': currency_eur.iso_code,
            'file': exchanges_csv
        }
        # deleting the field from `data`
        if missing_field == 'origin': 
            data.pop('origin')
        elif missing_field != 'target':
            data.pop('target')
        elif missing_field != 'file':
            data.pop('file')
        
        response = authenticated_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_upload_currency_exchanges_when_invalid_csv_returns_400(
            self, 
            authenticated_client, 
            currency_usd, 
            currency_eur):
        
        invalid_csv = SimpleUploadedFile(
            'rates.csv',
            b'Date,ExchangeRate\ninvalid_date,1.15',
            content_type='text/csv'
        )
        
        url = reverse('currencyexchange-upload')
        data = {
            'origin': currency_usd.iso_code,
            'target': currency_eur.iso_code,
            'file': invalid_csv
        }
        
        response = authenticated_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    @pytest.mark.parametrize("invalid_currency",
                            [("origin"),
                              ("target")
                            ])
    def test_upload_currency_exchanges_when_invalid_currency_returns_404(
        self, 
        authenticated_client, 
        currency_usd, 
        exchanges_csv, 
        invalid_currency: str):

        url = reverse('currencyexchange-upload')
        data = {
            'origin': 'BAD' if invalid_currency == "origin" else currency_usd.iso_code,
            'target': 'BAD' if invalid_currency == "target" else currency_usd.iso_code,
            'file': exchanges_csv
        }
        
        response = authenticated_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_bulk_delete_currency_exchanges_when_success_returns_200(
            self, 
            authenticated_client, 
            create_currency_exchange):
        
        exchange1= create_currency_exchange()
        exchange2= create_currency_exchange(date= exchange1.date - timedelta(days=1))
        
        url = reverse('currencyexchange-bulk-delete')
        url += f'?origin={exchange2.origin.iso_code}&target={exchange2.target.iso_code}'
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Successfully deleted 2 exchange rates'
        assert CurrencyExchange.objects.count() == 0

    def test_bulk_delete_currency_exchanges_when_missing_params_returns_400(self, authenticated_client):
        url = reverse('currencyexchange-bulk-delete')
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    @pytest.mark.parametrize("invalid_currency",
                            [("origin"),
                              ("target")
                            ])
    def test_bulk_delete_currency_exchanges_when_invalid_currency_returns_404(
        self, 
        authenticated_client, 
        currency_usd, 
        invalid_currency):

        origin = currency_usd.iso_code if invalid_currency != "origin" else 'BAD',
        target =  currency_usd.iso_code if invalid_currency != "target" else 'BAD',
        url = reverse('currencyexchange-bulk-delete')
        url += f'?origin={origin}&target={target}'
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND