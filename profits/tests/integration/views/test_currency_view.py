import pytest

from django.urls import reverse

from rest_framework import status

from profits.models import Currency

@pytest.mark.django_db
class TestCurrencyViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client, currency_gbp):
    #     url = reverse('currency-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_currencies_when_single_currency(self, authenticated_client, currency_gbp):
        url = reverse('currency-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['iso_code'] == currency_gbp.iso_code
        assert response.data[0]['description'] == currency_gbp.description
        assert len(response.data) == 1

    def test_list_currencies_when_multiple_currencies(self, authenticated_client, currency_gbp, currency_eur):
        url = reverse('currency-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_currency(self, authenticated_client, currency_gbp):
        url = reverse('currency-detail', args=[currency_gbp.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['iso_code'] == currency_gbp.iso_code
        assert response.data['description'] == currency_gbp.description

    def test_create_currency(self, authenticated_client):
        url = reverse('currency-list')
        data = {
            'iso_code': 'EUR',
            'description': 'EUR'
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['iso_code'] == data['iso_code']
        assert response.data['description'] == data['description']
        assert Currency.objects.count() == 1

    def test_delete_currency_when_has_no_entities_linked(self, authenticated_client, currency_gbp):
        url = reverse('currency-detail', args=[currency_gbp.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Currency.objects.filter(id=currency_gbp.id).exists()

    def test_delete_currency_when_has_origin_currencyexchange_linked(self, authenticated_client, currency_exchange_default):
        url = reverse('currency-detail', args=[currency_exchange_default.origin.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Currency.objects.filter(id=currency_exchange_default.origin.id).exists()

    def test_delete_currency_when_has_target_currencyexchange_linked(self, authenticated_client, currency_exchange_default):
        url = reverse('currency-detail', args=[currency_exchange_default.target.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Currency.objects.filter(id=currency_exchange_default.target.id).exists()

    def test_delete_currency_when_has_dividend_linked(self, authenticated_client, dividend_default):
        url = reverse('currency-detail', args=[dividend_default.currency.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Currency.objects.filter(id=dividend_default.currency.id).exists()

    def test_delete_currency_when_has_operation_linked(self, authenticated_client, operation_default):        
        url = reverse('currency-detail', args=[operation_default.currency.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Currency.objects.filter(id=operation_default.currency.id).exists()   

    def test_update_currency_when_called_returns_not_allowed(self, authenticated_client, currency_gbp):
        url = reverse('currency-detail', args=[currency_gbp.id])
        response = authenticated_client.put(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_partial_update_currency_when_called_returns_not_allowed(self, authenticated_client, currency_gbp):
        url = reverse('currency-detail', args=[currency_gbp.id])
        response = authenticated_client.patch(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
