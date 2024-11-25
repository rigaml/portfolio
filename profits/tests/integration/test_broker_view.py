import pytest

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from rest_framework.test import APIClient
from rest_framework import status

from profits.models import Account, Broker

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
def authenticated_client(api_client: APIClient, user: AbstractUser):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestBrokerViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client: APIClient, broker: Broker):
    #     url = reverse('broker-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_brokers_when_single_broker(self, authenticated_client: APIClient, broker: Broker):
        """
        'broker' parameter added, even not used in code, to trigger creation in fixture.
        """        
        url = reverse('broker-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_brokers_when_multiple_brokers(self, authenticated_client: APIClient, broker: Broker):
        """
        'broker' parameter added, even not used in code, to trigger creation in fixture.
        """
        Broker.objects.create(
            name='BRU',
            full_name='Test Broker 2'
        )

        url = reverse('broker-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_broker(self, authenticated_client: APIClient, broker: Broker):
        """
        'broker' parameter added, even not used in code, to trigger creation in fixture.
        """
        url = reverse('broker-detail', args=[broker.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == broker.name
        assert response.data['full_name'] == broker.full_name

    def test_create_broker(self, authenticated_client: APIClient, broker: Broker):
        url = reverse('broker-list')
        data = {
            'name': 'BRU',
            'full_name': 'Test Broker 2'
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
        assert response.data['full_name'] == data['full_name']
        assert Broker.objects.count() == 2

    def test_delete_broker_when_has_entities_linked(self, authenticated_client: APIClient, broker: Broker):
        url = reverse('broker-detail', args=[broker.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Broker.objects.filter(id=broker.id).exists()

    def test_delete_broker_when_has_accounts_linked(self, authenticated_client: APIClient, user: AbstractUser, broker: Broker):
        Account.objects.create(
            user=user,
            broker=broker,
            user_broker_ref='UserBrokerRef456',
            user_own_ref='UserOwnRef456'
        )
        
        url = reverse('broker-detail', args=[broker.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Broker.objects.filter(id=broker.id).exists()    