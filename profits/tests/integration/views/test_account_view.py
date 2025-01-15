import pytest

from datetime import datetime
from decimal import Decimal

from django.urls import reverse
from django.utils.timezone import make_aware

from rest_framework import status

from profits.models import Account

@pytest.mark.django_db
class TestAccountViewSet:

    # TODO: Add authentication tests
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
        params = {
            'user': user_default.id, 
            'broker': broker_default.id,
            'user_broker_ref': 'Create UserBrokerRef',
            'user_own_ref': 'Create UserOwnRef'
        }
        
        response = authenticated_client.post(url, params)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user'] == params['user']
        assert response.data['broker'] == params['broker']
        assert response.data['user_broker_ref'] == params['user_broker_ref']
        assert response.data['user_own_ref'] == params['user_own_ref']
        assert Account.objects.count() == 1

    def test_update_account(self, authenticated_client, account_default, user_default , broker_default):
        url = reverse('account-detail', args=[account_default.id])
        params = {
            'user': user_default.id, 
            'broker': broker_default.id,
            'user_broker_ref': 'Update UserBrokerRef',
            'user_own_ref': 'Update UserOwnRef'
        }
        
        response = authenticated_client.put(url, params)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == params['user']
        assert response.data['broker'] == params['broker']
        assert response.data['user_broker_ref'] == params['user_broker_ref']
        assert response.data['user_own_ref'] == params['user_own_ref']
        assert Account.objects.count() == 1

    def test_partial_update_account(self, authenticated_client, account_default, user_default , broker_default):
        url = reverse('account-detail', args=[account_default.id])
        params = {
            'user_own_ref': 'Update UserOwnRef'
        }
        
        response = authenticated_client.patch(url, params)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == user_default.id
        assert response.data['broker'] == broker_default.id
        assert response.data['user_broker_ref'] == account_default.user_broker_ref
        assert response.data['user_own_ref'] == params['user_own_ref']
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

    @pytest.mark.parametrize("invalid_field",
                            [("date_start"),
                             ("date_end"),
                             ("all"),
                            ])
    def test_total_when_invalid_dates(self, authenticated_client, account_default, invalid_field):
        url = reverse('account-total', args=[account_default.id])
        params = {
            'date_start': '2021-01-01T00:00:00',
            'date_end': '2023-12-31T23:59:59'
        }

        if invalid_field in ('date_start', 'all'):
            params['date_start']= 'invalid-date'
        if invalid_field in ('date_end', 'all'):
            params['date_end']= 'invalid-date'
        
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
        assert response.data['date_start'] == make_aware(datetime.fromisoformat(params['date_start']))
        assert response.data['date_end'] == make_aware(datetime.fromisoformat(params['date_end']))
        assert response.data['profit_total'] == Decimal(0)


    def test_total_when_no_dates(self, authenticated_client, account_default, operation_default):
        url = reverse('account-total', args=[account_default.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == account_default.id
        assert response.data['date_start'] is None
        assert response.data['date_end'] is None
        assert response.data['profit_total'] == Decimal(0)

    def test_total_details_account_when_not_found_returns_404(self, authenticated_client):
        url = reverse('account-total-details', args=[99999])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("invalid_field",
                            [("date_start"),
                             ("date_end"),
                             ("all"),
                            ])
    def test_total_details_when_invalid_dates(self, authenticated_client, account_default, invalid_field):
        url = reverse('account-total-details', args=[account_default.id])
        params = {
            'date_start': '2021-01-01T00:00:00',
            'date_end': '2023-12-31T23:59:59'
        }

        if invalid_field in ('date_start', 'all'):
            params['date_start']= 'invalid-date'
        if invalid_field in ('date_end', 'all'):
            params['date_end']= 'invalid-date'

        response = authenticated_client.get(url, params)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_total_details_when_valid_parameters(
            self, 
            authenticated_client, 
            account_default, 
            create_operation,
            create_date,
            currency_usd):
        
        url = reverse('account-total-details', args=[account_default.id])
        params = {
            'date_start': '2021-01-01T00:00:00',
            'date_end': '2025-12-31T23:59:59'
        }

        buy_operation = create_operation(
            account=account_default,
            type='BUY',
            date=create_date('2023-01-15'),
            ticker='AAPL',
            quantity=Decimal('100'),
            currency=currency_usd,
            amount_total=Decimal('10000'),
            exchange=Decimal('1.0')
        )
        
        sell_operation = create_operation(
            account=account_default,
            type='SELL',
            date=create_date('2023-06-01'),
            ticker='AAPL',
            quantity=Decimal('100'),
            currency=currency_usd,
            amount_total=Decimal('15000'),
            exchange=Decimal('1.0')
        )

        response = authenticated_client.get(url, params)
        
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment; filename=' in response['Content-Disposition']
        
        content = response.content.decode('utf-8')
        csv_lines = content.split('\n')
        assert len(csv_lines) == 3 # Header + data row + '\n' empty line at the end
        
        # Verify header
        header = csv_lines[0].split(',')
        last_column_index = len(header) - 1
        header[last_column_index] = header[last_column_index].strip()  # removes '\r' if added at the end of the line
        assert 'Ticker' in header
        assert 'Sell Date' in header
        assert 'Profit' in header
        
        # Verify data
        data_row = csv_lines[1].split(',')
        data_row[last_column_index] = data_row[last_column_index].strip()  # removes '\r' if added at the end of the line
        assert data_row[0] == buy_operation.ticker
        assert data_row[len(data_row) - 1] == f"{(sell_operation.amount_total - buy_operation.amount_total):.7f}"
        

    def test_total_details_when_no_dates(
            self, 
            authenticated_client, 
            account_default, 
            create_operation,
            create_date,
            currency_usd):            

        url = reverse('account-total-details', args=[account_default.id])

        buy_operation = create_operation(
            account=account_default,
            type='BUY',
            date=create_date('2023-01-15'),
            ticker='AAPL',
            quantity=Decimal('100'),
            currency=currency_usd,
            amount_total=Decimal('10000'),
            exchange=Decimal('1.0')
        )
        
        sell_operation = create_operation(
            account=account_default,
            type='SELL',
            date=create_date('2023-06-01'),
            ticker='AAPL',
            quantity=Decimal('100'),
            currency=currency_usd,
            amount_total=Decimal('15000'),
            exchange=Decimal('1.0')
        )    

        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment; filename=' in response['Content-Disposition']
        
        content = response.content.decode('utf-8')
        csv_lines = content.split('\n')
        assert len(csv_lines) == 3 # Header + data row + '\n' empty line at the end
