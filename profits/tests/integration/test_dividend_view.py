import pytest

from datetime import datetime

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import make_aware

from rest_framework.test import APIClient
from rest_framework import status

from profits.models import Account, Currency, Dividend

# Gets the active User model, in our case, one defined in `core.models.User`
User = get_user_model()

date_str = '2023-01-01'
date_start = make_aware(datetime.fromisoformat(date_str))

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
            iso_code = 'USD',
            description = 'USD'
        )

@pytest.fixture
def dividend(currency: Currency):
    return Dividend.objects.create(
        date= date_start,
        ticker='TSLA',
        currency=currency,
        amount_total=10.0
    )

@pytest.fixture
def authenticated_client(api_client: APIClient, user: AbstractUser):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestDividendViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client: APIClient, dividend: Dividend):
    #     url = reverse('dividend-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_dividends_when_single_dividend(self, authenticated_client: APIClient, dividend: Dividend):
        """
        'dividend' parameter added, even not used in code, to trigger creation in fixture.
        """        
        url = reverse('dividend-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_dividends_when_multiple_dividends(self, authenticated_client: APIClient, currency: Currency, dividend: Dividend):
        """
        'dividend' parameter added, even not used in code, to trigger creation in fixture.
        """
        Dividend.objects.create(
            date= make_aware(datetime.now()),
            ticker='AMZN',
            currency=currency,
            amount_total=10.0
            )

        url = reverse('dividend-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_dividend(self, authenticated_client: APIClient, dividend: Dividend):
        """
        'dividend' parameter added, even not used in code, to trigger creation in fixture.
        """
        url = reverse('dividend-detail', args=[dividend.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == date_str
        assert response.data['ticker'] == dividend.ticker
        assert response.data['currency'] == dividend.currency.iso_code
        assert response.data['amount_total'] == f"{dividend.amount_total:.7f}"

    def test_create_dividend(self, authenticated_client: APIClient, dividend: Dividend):
        url = reverse('dividend-list')
        data = {
            'date': '2023-01-01',
            'ticker': 'AMZN',
            'currency': dividend.currency.iso_code, 
            'amount_total': 10.0
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == data['date']
        assert response.data['ticker'] == data['ticker']
        assert response.data['currency'] == data['currency']
        assert response.data['amount_total'] == f"{data['amount_total']:.7f}"
        assert Dividend.objects.count() == 2

    def test_delete_split_when_has_no_entities_linked(self, authenticated_client: APIClient, dividend: Dividend):
        url = reverse('dividend-detail', args=[dividend.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Dividend.objects.filter(id=dividend.id).exists()
