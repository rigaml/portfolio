import pytest

from datetime import datetime

from django.urls import reverse

from rest_framework import status

from profits.models import Split

@pytest.mark.django_db
class TestSplitViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client, split):
    #     url = reverse('split-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_splits_when_single_split(self, authenticated_client, split_default):
        url = reverse('split-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['date'] == datetime.strftime(split_default.date, "%Y-%m-%d")
        assert response.data[0]['ticker'] == split_default.ticker
        assert len(response.data) == 1

    def test_list_splits_when_multiple_splits(self, authenticated_client, create_split):
        create_split(ticker="AAPL")
        create_split(ticker="GOOG")

        url = reverse('split-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_split(self, authenticated_client, split_default):
        url = reverse('split-detail', args=[split_default.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == datetime.strftime(split_default.date, "%Y-%m-%d")
        assert response.data['ticker'] == split_default.ticker
        assert response.data['origin'] == f"{split_default.origin:.2f}"
        assert response.data['target'] == f"{split_default.target:.2f}"

    def test_create_split(self, authenticated_client):
        url = reverse('split-list')
        data = {
            'date': '2023-01-01',
            'ticker': 'AMZN',
            'origin': 1.0,
            'target': 10.0
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == data['date']
        assert response.data['ticker'] == data['ticker']
        assert response.data['origin'] == f"{data['origin']:.2f}"
        assert response.data['target'] == f"{data['target']:.2f}"
        assert Split.objects.count() == 1

    def test_delete_split(self, authenticated_client, split_default):
        url = reverse('split-detail', args=[split_default.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Split.objects.filter(id=split_default.id).exists()
