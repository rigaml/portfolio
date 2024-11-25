import pytest

from typing import Callable

import io
import csv
from datetime import datetime

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from profits.models import CurrencyExchange
from profits.tests.conftest import create_currency, create_exchange


@pytest.fixture
def currency_usd(create_currency):
    return create_currency(iso_code='USD', description='US Dollar')

@pytest.fixture
def currency_eur(create_currency):
    return create_currency(iso_code='EUR', description='Euro')

@pytest.fixture
def currency_exchange(create_exchange, currency_usd, currency_eur):
    return create_exchange(
        date=datetime.strptime('01 Jan 23', '%d %b %y').date(),
        origin=currency_usd,
        target=currency_eur,
        rate=1.15
    )

@pytest.fixture
def csv_file():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'ExchangeRate'])
    writer.writerow(['01 Jan 23', '1.15'])
    writer.writerow(['02 Jan 23', '1.16'])
    
    return SimpleUploadedFile(
        'rates.csv',
        output.getvalue().encode('utf-8'),
        content_type='text/csv'
    )

@pytest.mark.django_db
class TestCurrencyExchangeViewSet:
    def test_list_exchanges(self, authenticated_client, currency_exchange):
        url = reverse('currencyexchange-list')
        response = authenticated_client().get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_retrieve_exchange(self, authenticated_client, currency_exchange):
        url = reverse('currencyexchange-detail', args=[currency_exchange.id])
        response = authenticated_client().get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == datetime.strftime(currency_exchange.date, "%Y-%m-%d")
        assert response.data['origin'] == currency_exchange.origin.iso_code
        assert response.data['target'] == currency_exchange.target.iso_code
        assert response.data['rate'] == '1.150000'

    def test_upload_exchange_rates_success(self, authenticated_client, currency_usd, currency_eur, csv_file):
        url = reverse('currencyexchange-upload')
        data = {
            'origin': currency_usd.iso_code,
            'target': currency_eur.iso_code,
            'file': csv_file
        }
        
        response = authenticated_client().post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Successfully imported 2 exchange rates'
        assert CurrencyExchange.objects.count() == 2

    @pytest.mark.parametrize("missing_field",
                            [("origin"),
                              ("target"),
                              ("file")
                            ])
    def test_upload_exchange_rates_missing_fields(self, authenticated_client, currency_usd, currency_eur, csv_file, missing_field):
        url = reverse('currencyexchange-upload')
        data = {
            'origin': currency_usd.iso_code,
            'target': currency_eur.iso_code,
            'file': csv_file
        }
        if missing_field == 'origin': 
            data.pop('origin')
        elif missing_field != 'target':
            data.pop('target')
        elif missing_field != 'file':
            data.pop('file')
        
        response = authenticated_client().post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_upload_exchange_rates_invalid_csv(self, authenticated_client, currency_usd, currency_eur):
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
        
        response = authenticated_client().post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    @pytest.mark.parametrize("invalid_currency",
                            [("origin"),
                              ("target")
                            ])
    def test_upload_exchange_rates_invalid_currency(self, authenticated_client, currency_usd, csv_file, invalid_currency: str):
        url = reverse('currencyexchange-upload')
        data = {
            'origin': 'BAD' if invalid_currency == "origin" else currency_usd.iso_code,
            'target': 'BAD' if invalid_currency == "target" else currency_usd.iso_code,
            'file': csv_file
        }
        
        response = authenticated_client().post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_bulk_delete_success(self, authenticated_client, currency_exchange, currency_usd, currency_eur):
        # Create another exchange rate
        CurrencyExchange.objects.create(
            date=datetime.strptime('02 Jan 23', '%d %b %y').date(),
            origin=currency_usd,
            target=currency_eur,
            rate=1.16
        )
        
        url = reverse('currencyexchange-bulk-delete')
        url += f'?origin={currency_usd.iso_code}&target={currency_eur.iso_code}'
        
        response = authenticated_client().delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Successfully deleted 2 exchange rates'
        assert CurrencyExchange.objects.count() == 0

    def test_bulk_delete_missing_params(self, authenticated_client):
        url = reverse('currencyexchange-bulk-delete')
        response = authenticated_client().delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    @pytest.mark.parametrize("invalid_currency",
                            [("origin"),
                              ("target")
                            ])
    def test_bulk_delete_invalid_currency(self, authenticated_client, currency_usd, invalid_currency: str):
        origin = currency_usd.iso_code if invalid_currency != "origin" else 'BAD',
        target =  currency_usd.iso_code if invalid_currency != "target" else 'BAD',
        url = reverse('currencyexchange-bulk-delete')
        url += f'?origin={origin}&target={target}'
        
        response = authenticated_client().delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND