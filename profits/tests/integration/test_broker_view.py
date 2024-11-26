import pytest

from django.urls import reverse

from rest_framework import status

from profits.models import Broker

@pytest.mark.django_db
class TestBrokerViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client, broker_default):
    #     url = reverse('broker-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_brokers_when_single_broker(self, authenticated_client, broker_default):
        url = reverse('broker-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['name'] == broker_default.name
        assert response.data[0]['full_name'] == broker_default.full_name
        assert len(response.data) == 1

    def test_list_brokers_when_multiple_brokers(self, authenticated_client, create_broker):
        create_broker(name="BRO")
        create_broker(name="BRU")

        url = reverse('broker-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_broker(self, authenticated_client, broker_default):
        url = reverse('broker-detail', args=[broker_default.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == broker_default.name
        assert response.data['full_name'] == broker_default.full_name

    def test_create_broker(self, authenticated_client):
        url = reverse('broker-list')
        data = {
            'name': 'BRU',
            'full_name': 'Test Broker 2'
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
        assert response.data['full_name'] == data['full_name']
        assert Broker.objects.count() == 1

    def test_delete_broker_when_has_entities_linked(self, authenticated_client, broker_default):
        url = reverse('broker-detail', args=[broker_default.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Broker.objects.filter(id=broker_default.id).exists()

    def test_delete_broker_when_has_accounts_linked(self, authenticated_client, broker_default, account_default):
        """
        When `account_default` is created points to `broker_default`
        """        
        url = reverse('broker-detail', args=[broker_default.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Broker.objects.filter(id=broker_default.id).exists()    