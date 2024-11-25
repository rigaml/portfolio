import pytest

from datetime import datetime

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import make_aware

from rest_framework.test import APIClient
from rest_framework import status

from profits.models import Account, Broker, Currency, CurrencyExchange, Dividend, Operation

# Gets the active User model, in our case, one defined in `core.models.User`
User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def currency():
    return Currency.objects.create(
            iso_code = 'GBP',
            description = 'GBP'
        )

@pytest.fixture
def authenticated_client(api_client: APIClient, user: AbstractUser):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestCurrencyViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client: APIClient, currency: Currency):
    #     url = reverse('currency-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_currencies_when_single_currency(self, authenticated_client: APIClient, currency: Currency):
        """
        'currency' parameter added, even not used in code, to trigger creation in fixture.
        """        
        url = reverse('currency-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_currencies_when_multiple_currencies(self, authenticated_client: APIClient, currency: Currency):
        """
        'currency' parameter added, even not used in code, to trigger creation in fixture.
        """
        Currency.objects.create(
            iso_code = 'EUR',
            description = 'EUR'
        )

        url = reverse('currency-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_currency(self, authenticated_client: APIClient, currency: Currency):
        """
        'currency' parameter added, even not used in code, to trigger creation in fixture.
        """
        url = reverse('currency-detail', args=[currency.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['iso_code'] == currency.iso_code
        assert response.data['description'] == currency.description

    def test_create_currency(self, authenticated_client: APIClient, currency: Currency):
        url = reverse('currency-list')
        data = {
            'iso_code': 'EUR',
            'description': 'EUR'
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['iso_code'] == data['iso_code']
        assert response.data['description'] == data['description']
        assert Currency.objects.count() == 2

    def test_delete_currency_when_has_no_entities_linked(self, authenticated_client: APIClient, currency: Currency):
        url = reverse('currency-detail', args=[currency.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Currency.objects.filter(id=currency.id).exists()

    def test_delete_currency_when_has_origin_currencyexchange_linked(self, authenticated_client: APIClient, currency: Currency):
        other_currency= Currency.objects.create(
            iso_code = 'EUR',
            description = 'EUR'
        )
        CurrencyExchange.objects.create(
            date= make_aware(datetime.now()),
            origin= currency,
            target= other_currency,
            rate= 1.25
        )
        
        url = reverse('currency-detail', args=[currency.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Currency.objects.filter(id=currency.id).exists()

    def test_delete_currency_when_has_target_currencyexchange_linked(self, authenticated_client: APIClient, currency: Currency):
        other_currency= Currency.objects.create(
            iso_code = 'EUR',
            description = 'EUR'
        )
        CurrencyExchange.objects.create(
            date= make_aware(datetime.now()),
            origin= other_currency,
            target= currency,
            rate= 1.25
        )
        
        url = reverse('currency-detail', args=[currency.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Currency.objects.filter(id=currency.id).exists()     

    def test_delete_currency_when_has_dividend_linked(self, authenticated_client: APIClient, currency: Currency):
        Dividend.objects.create(
            date= make_aware(datetime.now()),
            ticker= "TSLA",
            currency= currency,
            amount_total= 125
        )
        
        url = reverse('currency-detail', args=[currency.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Currency.objects.filter(id=currency.id).exists()                 

    def test_delete_currency_when_has_operation_linked(self, authenticated_client: APIClient, user: AbstractUser, currency: Currency):
        broker= Broker.objects.create(
            name='BRO',
            full_name='Test Broker'
        )
        account= Account.objects.create(
                user=user,
                broker=broker,
                user_broker_ref='UserBrokerRef123',
                user_own_ref='UserOwnRef456'
            )
        Operation.objects.create(
            account=account,
            date=make_aware(datetime.now()),
            type= Operation.TYPE_CHOICES[0][0],
            ticker= 'TSLA',
            quantity= 10.0,
            currency= currency,
            amount_total = 10000,
            exchange = 1
        )
        
        url = reverse('currency-detail', args=[currency.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Currency.objects.filter(id=currency.id).exists()   