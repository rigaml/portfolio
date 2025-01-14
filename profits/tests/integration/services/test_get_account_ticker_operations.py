import pytest

from datetime import datetime, timezone

from profits.services.operation_service import OperationService


@pytest.fixture
def sample_operations(create_operation, create_account, create_user, create_date):
    create_operation(date=create_date('2024-01-01'))
    create_operation(date=create_date('2024-02-02'))
    create_operation(date=create_date('2024-03-03'))

    # Create operations for other tickers
    create_operation(ticker="TSLA", date=create_date('2024-01-01'))
    create_operation(ticker="MSFT", date=create_date('2024-01-01'))

    # Creates operations for non-default account
    other_account=create_account(user=create_user(username="another"))
    create_operation(account=other_account, date=create_date('2024-01-01'))
    create_operation(account=other_account, date=create_date('2024-01-02'))


@pytest.mark.django_db
class TestGetAccountTickerOperations:
        
    def test_when_no_date_end_then_returns_default_account_all_operations(self, account_default, sample_operations):
        
        operation_service = OperationService()
        result = operation_service.get_account_ticker_operations(account_default, 'AAPL', None)
        
        assert len(result) == 3
        assert list(result) == sorted(result, key=lambda x: x.date)

    def test_when_filtered_by_date_end_then_returns_default_account_previous_operations(self, account_default, sample_operations):
        date_end = datetime(2024, 3, 1, tzinfo=timezone.utc)

        operation_service = OperationService()
        result = operation_service.get_account_ticker_operations(account_default, 'AAPL', date_end)
        
        assert len(result) == 2

    def test_when_account_without_operations_then_returns_no_operations(self, create_account, sample_operations):
        account_without_operations = create_account()

        operation_service = OperationService()
        result = operation_service.get_account_ticker_operations(account_without_operations, 'AAPL', None)
        
        assert len(result) == 0
