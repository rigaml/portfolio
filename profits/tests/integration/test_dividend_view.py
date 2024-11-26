import pytest

from datetime import datetime

from django.urls import reverse

from rest_framework import status

from profits.models import Dividend

@pytest.mark.django_db
class TestDividendViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client, dividend):
    #     url = reverse('dividend-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_dividends_when_single_dividend(self, authenticated_client, dividend_default):
        url = reverse('dividend-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['date'] == datetime.strftime(dividend_default.date, "%Y-%m-%d")
        assert response.data[0]['ticker'] == dividend_default.ticker
        assert len(response.data) == 1

    def test_list_dividends_when_multiple_dividends(self, authenticated_client, create_dividend):
        create_dividend(ticker="AAPL")
        create_dividend(ticker="GOOG")

        url = reverse('dividend-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_dividend(self, authenticated_client, dividend_default):
        url = reverse('dividend-detail', args=[dividend_default.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == datetime.strftime(dividend_default.date, "%Y-%m-%d")
        assert response.data['ticker'] == dividend_default.ticker
        assert response.data['currency'] == dividend_default.currency.iso_code
        assert response.data['amount_total'] == f"{dividend_default.amount_total:.7f}"

    def test_create_dividend(self, authenticated_client, currency_gbp):
        url = reverse('dividend-list')
        data = {
            'date': '2023-01-01',
            'ticker': 'AMZN',
            'currency': currency_gbp.iso_code, 
            'amount_total': 10.0
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == data['date']
        assert response.data['ticker'] == data['ticker']
        assert response.data['currency'] == data['currency']
        assert response.data['amount_total'] == f"{data['amount_total']:.7f}"
        assert Dividend.objects.count() == 1

    def test_delete_dividend(self, authenticated_client, dividend_default):
        url = reverse('dividend-detail', args=[dividend_default.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Dividend.objects.filter(id=dividend_default.id).exists()
