import pytest

from datetime import datetime
from decimal import Decimal

from django.urls import reverse
from django.utils.timezone import make_aware

from rest_framework import status

from profits.models import Account

@pytest.mark.django_db
class TestAccountViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client: APIClient, account: Account):
    #     url = reverse('account-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_accounts_when_single_account(self, authenticated_client, account_default):
        url = reverse('account-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['user_broker_ref'] == account_default.user_broker_ref
        assert response.data[0]['user_own_ref'] == account_default.user_own_ref
        assert len(response.data) == 1

    def test_list_accounts_when_multiple_accounts(self, authenticated_client, create_account, user_default, broker_default):
        create_account()
        create_account()

        url = reverse('account-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


    def test_retrieve_account(self, authenticated_client, account_default):
        url = reverse('account-detail', args=[account_default.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_broker_ref'] == account_default.user_broker_ref
        assert response.data['user_own_ref'] == account_default.user_own_ref

    def test_create_account(self, authenticated_client, user_default , broker_default):
        url = reverse('account-list')
        data = {
            'user': user_default.id, 
            'broker': broker_default.id,
            'user_broker_ref': 'Create UserBrokerRef',
            'user_own_ref': 'Create UserOwnRef'
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user'] == data['user']
        assert response.data['broker'] == data['broker']
        assert response.data['user_broker_ref'] == data['user_broker_ref']
        assert response.data['user_own_ref'] == data['user_own_ref']
        assert Account.objects.count() == 1

    def test_update_account(self, authenticated_client, account_default, user_default , broker_default):
        url = reverse('account-detail', args=[account_default.id])
        data = {
            'user': user_default.id, 
            'broker': broker_default.id,
            'user_broker_ref': 'Update UserBrokerRef',
            'user_own_ref': 'Update UserOwnRef'
        }
        
        response = authenticated_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == data['user']
        assert response.data['broker'] == data['broker']
        assert response.data['user_broker_ref'] == data['user_broker_ref']
        assert response.data['user_own_ref'] == data['user_own_ref']
        assert Account.objects.count() == 1

    def test_partial_update_account(self, authenticated_client, account_default, user_default , broker_default):
        url = reverse('account-detail', args=[account_default.id])
        data = {
            'user_own_ref': 'Update UserOwnRef'
        }
        
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == user_default.id
        assert response.data['broker'] == broker_default.id
        assert response.data['user_broker_ref'] == account_default.user_broker_ref
        assert response.data['user_own_ref'] == data['user_own_ref']
        assert Account.objects.count() == 1
        
    def test_delete_account_when_has_no_entities_linked(self, authenticated_client, account_default):
        url = reverse('account-detail', args=[account_default.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Account.objects.filter(id=account_default.id).exists()

    def test_delete_account_when_has_operations_linked(self, authenticated_client, account_default, operation_default):
        """
        When `operation_default` is created points to `account_default`
        """
        url = reverse('account-detail', args=[account_default.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert Account.objects.filter(id=account_default.id).exists()

    def test_total_account_when_not_found_returns_404(self, authenticated_client):
        url = reverse('account-total', args=[99999])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_total_when_invalid_dates(self, authenticated_client, account_default):
        url = reverse('account-total', args=[account_default.id])
        params = {
            'date_start': 'invalid-date',
            'date_end': '2023-12-31T23:59:59'
        }
        
        response = authenticated_client.get(url, params)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_total_when_valid_parameters(self, authenticated_client, account_default, operation_default):
        url = reverse('account-total', args=[account_default.id])
        params = {
            'date_start': '2021-01-01T00:00:00',
            'date_end': '2025-12-31T23:59:59'
        }
        
        response = authenticated_client.get(url, params)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == account_default.id
        assert response.data['amount_total'] == Decimal(10000)
        assert response.data['date_start'] == make_aware(datetime.fromisoformat(params['date_start']))
        assert response.data['date_end'] == make_aware(datetime.fromisoformat(params['date_end']))


    def test_total_when_no_dates(self, authenticated_client, account_default, operation_default):
        url = reverse('account-total', args=[account_default.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == account_default.id
        assert response.data['amount_total'] == Decimal(10000)
        assert response.data['date_start'] is None
        assert response.data['date_end'] is None

    def test_total_details_account_when_not_found_returns_404(self, authenticated_client):
        url = reverse('account-total-details', args=[99999])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_total_details_when_invalid_dates(self, authenticated_client, account_default):
        url = reverse('account-total-details', args=[account_default.id])
        params = {
            'date_start': 'invalid-date',
            'date_end': '2023-12-31T23:59:59'
        }
        
        response = authenticated_client.get(url, params)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_total_details_when_valid_parameters(self, authenticated_client, account_default, mocker):
        url = reverse('account-total-details', args=[account_default.id])
        params = {
            'date_start': '2021-01-01T00:00:00',
            'date_end': '2025-12-31T23:59:59'
        }

        mock_total_details = [{
                'ticker': 'AAPL',
                'profit_detail': [{
                    'date': '2023-06-01',
                    'quantity': 100,
                    'amount_total': 15000,
                    'currency': 'USD',
                    'buy_date': '2023-01-15',
                    'buy_quantity': 100,
                    'buy_amount_total': 10000,
                    'profit': 5000
                }]
        }]

        from profits.services.operation_service import get_total_details
        print("Original function:", get_total_details)


        mock= mocker.patch('profits.services.operation_service.get_total_details')        
        mock.return_value=mock_total_details

        print("Mocked function:", mock)

        response = authenticated_client.get(url, params)
        
        print("Mock calls:", mock.call_args_list)
        assert mock.called

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment; filename=' in response['Content-Disposition']
        
        content = response.content.decode('utf-8')
        csv_lines = content.split('\n')
        assert len(csv_lines) == 2  # Header + at least one data row
        
        # Verify header
        header = csv_lines[0].split(',')
        header[len(header) - 1] = header[len(header) - 1].strip()  # removes '\r' if added at the end of the line
        assert 'Ticker' in header
        assert 'Sell Date' in header
        assert 'Profit' in header
        
        # Verify data
        data_row = csv_lines[1].split(',')
        assert data_row[0] == 'AAPL'
        assert data_row[len(data_row) - 1] == '5000'
        

    def test_total_details_when_no_dates(self, authenticated_client, account_default, mocker):
        url = reverse('account-total-details', args=[account_default.id])

        mock_total_details = [{
                'ticker': 'AAPL',
                'profit_detail': [{
                    'date': '2023-06-01',
                    'quantity': 100,
                    'amount_total': 15000,
                    'currency': 'USD',
                    'buy_date': '2023-01-15',
                    'buy_quantity': 100,
                    'buy_amount_total': 10000,
                    'profit': 5000
                }]
        }]
        mocker.patch('profits.services.operation_service.get_total_details', return_value=mock_total_details)      

        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment; filename=' in response['Content-Disposition']
        
        content = response.content.decode('utf-8')
        csv_lines = content.split('\n')
        assert len(csv_lines) == 2  # Header + at least one data row
        
        # Verify header
        header = csv_lines[0].split(',')
        header[len(header) - 1] = header[len(header) - 1].strip()  # removes '\r' if added at the end of the line
        assert 'Ticker' in header
        assert 'Sell Date' in header
        assert 'Profit' in header
        
        # Verify data
        data_row = csv_lines[1].split(',')
        assert data_row[0] == 'AAPL'
        assert data_row[len(data_row) - 1] == '5000'
