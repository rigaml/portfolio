import pytest

import io
import csv

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from profits.models import Operation

@pytest.fixture
def operations_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Type', 'Date', 'Quantity', 'Ticker', 'Amount Total', 'Currency'])
    writer.writerow(['BUY', '2023-06-01', 10, 'GOOG', 1000, 'USD'])
    writer.writerow(['SELL', '2024-01-01', 10, 'GOOG', 2000, 'USD'])
    
    return SimpleUploadedFile(
        'operations.csv',
        output.getvalue().encode('utf-8'),
        content_type='text/csv'
    )

@pytest.mark.django_db
class TestOperationViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client: APIClient, operation: Operation):
    #     url = reverse('operation-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_operations_when_single_operation(self, authenticated_client, operation_default):
        url = reverse('operation-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_operations_when_multiple_operations(
            self, 
            authenticated_client, 
            create_operation,
            date_factory):
        create_operation()
        create_operation(date=date_factory('2024-02-01'))

        url = reverse('operation-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_operation(self, authenticated_client, operation_default, date_default):
        url = reverse('operation-detail', args=[operation_default.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == date_default.isoformat().replace('+00:00', 'Z')
        assert response.data['type'] == operation_default.type
        assert response.data['ticker'] == operation_default.ticker
        assert response.data['quantity'] == f"{operation_default.quantity:.7f}"
        assert response.data['currency'] == operation_default.currency.iso_code
        assert response.data['amount_total'] == f"{operation_default.amount_total:.7f}"
        assert response.data['exchange'] == f"{operation_default.exchange:.6f}"

    def test_create_operation(self, authenticated_client, account_default, currency_gbp, operation_default, date_factory):
        url = reverse('operation-list')
        date_create = date_factory('2024-02-01')
        data = {
            'account': account_default.id,
            'date': date_create,
            'type': operation_default.TYPE_CHOICES[0][0],
            'ticker': 'AMZN',
            'quantity': 10,
            'currency': currency_gbp.iso_code,
            'amount_total': 100,
            'exchange': 1
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == date_create.isoformat().replace('+00:00', 'Z')
        assert response.data['type'] == data['type']
        assert response.data['ticker'] == data['ticker']
        assert response.data['quantity'] == f"{data['quantity']:.7f}"
        assert response.data['currency'] == data['currency']
        assert response.data['amount_total'] == f"{data['amount_total']:.7f}"
        assert response.data['exchange'] == f"{data['exchange']:.6f}"
        assert Operation.objects.count() == 2

    def test_delete_operation_when_has_no_entities_linked(self, authenticated_client, operation_default):
        url = reverse('operation-detail', args=[operation_default.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Operation.objects.filter(id=operation_default.id).exists()

    def test_update_operation_when_called_returns_not_allowed(self, authenticated_client, operation_default):
        url = reverse('operation-detail', args=[operation_default.id])
        response = authenticated_client.put(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_partial_update_operation_when_called_returns_not_allowed(self, authenticated_client, operation_default):
        url = reverse('operation-detail', args=[operation_default.id])
        response = authenticated_client.patch(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_upload_operations_success(self, authenticated_client, account_default, currency_usd, operations_csv):
        """
        Parameter `currency_usd` required so it is created in DB.
        """
        url = reverse('operation-upload')
        data = {
            'account_id': account_default.id,
            'file': operations_csv
        }
        
        response = authenticated_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Successfully imported 2 operations'
        assert Operation.objects.count() == 2

    @pytest.mark.parametrize("missing_field",
                            [("account_id"),
                              ("file")
                            ])
    def test_upload_operations_missing_fields(self, authenticated_client, account_default, operations_csv, missing_field):
        url = reverse('operation-upload')
        data = {
            'account_id': account_default.id,
            'file': operations_csv
        }
        if missing_field == 'account_id': 
            data.pop('account_id')
        elif missing_field != 'file':
            data.pop('file')
        
        response = authenticated_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_upload_operations_invalid_csv(self, authenticated_client, account_default):
        invalid_csv = SimpleUploadedFile(
            'operation_cut.csv',
            b'Type,Date\n"BUY", "2023-06-01"',
            content_type='text/csv'
        )
        
        url = reverse('operation-upload')
        data = {
            'account_id': account_default.id,
            'file': invalid_csv
        }
        
        response = authenticated_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_upload_operations_invalid_account_id(self, authenticated_client, account_default, operations_csv):
        url = reverse('operation-upload')
        data = {
            'account_id': account_default.id + 1,
            'file': operations_csv
        }
        
        response = authenticated_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_bulk_delete_operations_success(self, authenticated_client, account_default, create_operation):
        operation1= create_operation()
        operation2= create_operation(ticker= operation1.ticker + "O")
        
        url = reverse('operation-bulk-delete')
        url += f'?account_id={account_default.id}'
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Successfully deleted 2 operations'
        assert Operation.objects.count() == 0

    def test_bulk_delete_operations_missing_params(self, authenticated_client):
        url = reverse('operation-bulk-delete')
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_bulk_delete_operations_invalid_account_id(self, authenticated_client, account_default):
        url = reverse('operation-bulk-delete')
        url += f'?account_id={(account_default.id + 1)}'
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND        

