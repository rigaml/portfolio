import pytest

import io
import csv

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from profits.models import Split

@pytest.fixture
def splits_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Ticker', 'Date', 'Origin', 'Target'])
    writer.writerow(['APPL', '2023-06-01', 1, 10])
    writer.writerow(['GOOG', '2024-01-01', 2, 15])
    
    return SimpleUploadedFile(
        'splits.csv',
        output.getvalue().encode('utf-8'),
        content_type='text/csv'
    )

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
        assert response.data[0]['date'] == split_default.date.date().isoformat()
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
        assert response.data['date'] == split_default.date.date().isoformat()
        assert response.data['ticker'] == split_default.ticker
        assert response.data['origin'] == f"{split_default.origin:.2f}"
        assert response.data['target'] == f"{split_default.target:.2f}"

    def test_create_split(self, authenticated_client):
        url = reverse('split-list')
        params = {
            'date': '2023-01-01',
            'ticker': 'AMZN',
            'origin': 1.0,
            'target': 10.0
        }
        
        response = authenticated_client.post(url, params)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == params['date']
        assert response.data['ticker'] == params['ticker']
        assert response.data['origin'] == f"{params['origin']:.2f}"
        assert response.data['target'] == f"{params['target']:.2f}"
        assert Split.objects.count() == 1

    def test_delete_split(self, authenticated_client, split_default):
        url = reverse('split-detail', args=[split_default.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Split.objects.filter(id=split_default.id).exists()

    def test_update_split_when_called_returns_not_allowed(self, authenticated_client, split_default):
        url = reverse('split-detail', args=[split_default.id])
        response = authenticated_client.put(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_partial_update_split_when_called_returns_not_allowed(self, authenticated_client, split_default):
        url = reverse('split-detail', args=[split_default.id])
        response = authenticated_client.patch(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_upload_splits_success(self, authenticated_client, splits_csv):
        url = reverse('split-upload')
        params = {
            'file': splits_csv
        }
        
        response = authenticated_client.post(url, params, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Successfully imported 2 splits'
        assert Split.objects.count() == 2


    def test_upload_splits_missing_fields(self, authenticated_client, splits_csv):
        url = reverse('split-upload')
        params = { }
        
        response = authenticated_client.post(url, params, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_upload_splits_invalid_csv(self, authenticated_client):
        invalid_csv = SimpleUploadedFile(
            'split_cut.csv',
            b'"Date", "Origin", "Target"\n"2023-06-01", 1, 10',
            content_type='text/csv'
        )
        
        url = reverse('split-upload')
        params = {
            'file': invalid_csv
        }
        
        response = authenticated_client.post(url, params, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_bulk_delete_split_success(self, authenticated_client, create_split):
        split1= create_split()
        split2= create_split(ticker= split1.ticker + "O")
        
        url = reverse('split-bulk-delete')
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Successfully deleted 2 splits'
        assert Split.objects.count() == 0
