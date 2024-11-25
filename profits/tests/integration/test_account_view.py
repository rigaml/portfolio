import pytest

from datetime import datetime

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import make_aware

from rest_framework.test import APIClient
from rest_framework import status

from profits.models import Account, Broker, Currency, Operation

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
def broker():
    return Broker.objects.create(
        name='BRO',
        full_name='Test Broker'
    )

@pytest.fixture
def account(user: AbstractUser, broker: Broker):
    return Account.objects.create(
        user=user,
        broker=broker,
        user_broker_ref='UserBrokerRef123',
        user_own_ref='UserOwnRef456'
    )

@pytest.fixture
def authenticated_client(api_client: APIClient, user: AbstractUser):
    api_client.force_authenticate(user=user)
    return api_client
    
@pytest.mark.django_db
class TestAccountViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client: APIClient, account: Account):
    #     url = reverse('account-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_accounts_when_single_account(self, authenticated_client: APIClient, account: Account):
        """
        'account' parameter added, even not used in code, to trigger creation in fixture.
        """
        url = reverse('account-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_accounts_when_multiple_accounts(self, authenticated_client: APIClient, account: Account, user: AbstractUser, broker: Broker):
        """
        'account' parameter added, even not used in code, to trigger creation in fixture.
        """
        Account.objects.create(
            user=user,
            broker=broker,
            user_broker_ref='UserBrokerRef456',
            user_own_ref='UserOwnRef456'
        )

        url = reverse('account-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


    def test_retrieve_account(self, authenticated_client: APIClient, account: Account):
        """
        'account' parameter added, even not used in code, to trigger creation in fixture.
        """
        url = reverse('account-detail', args=[account.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_broker_ref'] == account.user_broker_ref
        assert response.data['user_own_ref'] == account.user_own_ref

    def test_create_account(self, authenticated_client: APIClient, user: AbstractUser , broker: Broker):
        url = reverse('account-list')
        data = {
            'user': user.id, 
            'broker': broker.id,
            'user_broker_ref': 'NEW123',
            'user_own_ref': 'MyNewAccount'
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user'] == data['user']
        assert response.data['broker'] == data['broker']
        assert response.data['user_broker_ref'] == data['user_broker_ref']
        assert response.data['user_own_ref'] == data['user_own_ref']
        assert Account.objects.count() == 1

    def test_delete_account_when_has_no_entities_linked(self, authenticated_client: APIClient, account: Account):
        url = reverse('account-detail', args=[account.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Account.objects.filter(id=account.id).exists()

    def test_delete_account_when_has_operations_linked(self, authenticated_client: APIClient, account: Account):
        currency= Currency.objects.create(
            iso_code = 'GBP',
            description = 'GBP'
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
        
        url = reverse('account-detail', args=[account.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Account.objects.filter(id=account.id).exists()

    def test_total_when_valid_parameters(self, authenticated_client: APIClient, account: Account):
        url = reverse('account-total', args=[account.id])
        params = {
            'date_start': '2023-01-01T00:00:00',
            'date_end': '2023-12-31T23:59:59'
        }
        
        response = authenticated_client.get(url, params)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == account.id
        assert response.data['amount_total'] == 10000
        assert response.data['date_start'] == datetime.fromisoformat(params['date_start'])
        assert response.data['date_end'] == datetime.fromisoformat(params['date_end'])

    def test_total_when_invalid_dates(self, authenticated_client: APIClient, account: Account):
        url = reverse('account-total', args=[account.id])
        params = {
            'date_start': 'invalid-date',
            'date_end': '2023-12-31'
        }
        
        response = authenticated_client.get(url, params)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == account.id
        assert response.data['amount_total'] == 10000
        assert response.data['date_start'] is None
        assert response.data['date_end'] == datetime.fromisoformat(params['date_end'])

    def test_total_when_no_dates(self, authenticated_client: APIClient, account: Account):
        url = reverse('account-total', args=[account.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == account.id
        assert response.data['amount_total'] == 10000
        assert response.data['date_start'] is None
        assert response.data['date_end'] is None

    def test_total_account_not_found(self, authenticated_client: APIClient):
        url = reverse('account-total', args=[99999])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
