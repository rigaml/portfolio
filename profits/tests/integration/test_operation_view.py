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

date_str = '2023-01-01T00:00:00'
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
def currency():
    return Currency.objects.create(
            iso_code = 'USD',
            description = 'USD'
        )

@pytest.fixture
def operation(account: Account, currency: Currency):
    return Operation.objects.create(
        account= account,
        date= date_start,
        type=Operation.TYPE_CHOICES[0][0],
        ticker='TSLA',
        quantity= 10,
        currency= currency,
        amount_total= 100,
        exchange= 1
    )

@pytest.fixture
def authenticated_client(api_client: APIClient, user: AbstractUser):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestOperationViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client: APIClient, operation: Operation):
    #     url = reverse('operation-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_operations_when_single_operation(self, authenticated_client: APIClient, operation: Operation):
        """
        'operation' parameter added, even not used in code, to trigger creation in fixture.
        """        
        url = reverse('operation-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_operations_when_multiple_operations(self, authenticated_client: APIClient, account: Account, currency: Currency, operation: Operation):
        """
        'operation' parameter added, even not used in code, to trigger creation in fixture.
        """
        Operation.objects.create(
            account= account,
            date= date_start,
            type=Operation.TYPE_CHOICES[0][0],
            ticker='AMZN',
            quantity= 10,
            currency= currency,
            amount_total= 100,
            exchange= 1
            )

        url = reverse('operation-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_operation(self, authenticated_client: APIClient, operation: Operation):
        """
        'operation' parameter added, even not used in code, to trigger creation in fixture.
        """
        url = reverse('operation-detail', args=[operation.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == date_start.isoformat().replace('+00:00', 'Z')
        assert response.data['type'] == operation.type
        assert response.data['ticker'] == operation.ticker
        assert response.data['quantity'] == f"{operation.quantity:.7f}"
        assert response.data['currency'] == operation.currency.iso_code
        assert response.data['amount_total'] == f"{operation.amount_total:.7f}"
        assert response.data['exchange'] == f"{operation.exchange:.6f}"

    def test_create_operation(self, authenticated_client: APIClient, account: Account, currency: Currency, operation: Operation):
        url = reverse('operation-list')
        data = {
            'account': account.id,
            'date': date_start,
            'type': Operation.TYPE_CHOICES[0][0],
            'ticker': 'AMZN',
            'quantity': 10,
            'currency': currency.iso_code,
            'amount_total': 100,
            'exchange': 1
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == date_start.isoformat().replace('+00:00', 'Z')
        assert response.data['type'] == data['type']
        assert response.data['ticker'] == data['ticker']
        assert response.data['quantity'] == f"{data['quantity']:.7f}"
        assert response.data['currency'] == data['currency']
        assert response.data['amount_total'] == f"{data['amount_total']:.7f}"
        assert response.data['exchange'] == f"{data['exchange']:.6f}"
        assert Operation.objects.count() == 2

    def test_delete_operation_when_has_no_entities_linked(self, authenticated_client: APIClient, operation: Operation):
        url = reverse('operation-detail', args=[operation.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Operation.objects.filter(id=operation.id).exists()

    def test_update_operation(self, authenticated_client: APIClient, operation: Operation):
        url = reverse('operation-detail', args=[operation.id])
        response = authenticated_client.put(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_partial_update_operation(self, authenticated_client: APIClient, operation: Operation):
        url = reverse('operation-detail', args=[operation.id])
        response = authenticated_client.patch(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

