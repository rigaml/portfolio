from unittest.mock import Mock
import pytest

from datetime import datetime, timezone

from profits.tests.conftest import create_date
from profits.services.profit_service import ProfitService
from profits.services.currency_service import CurrencyService
from profits.services.operation_service import OperationService


@pytest.fixture
def sample_operations(create_operation, create_date):
    create_operation(date=create_date('2024-01-01'))
    create_operation(date=create_date('2024-02-02'))
    create_operation(date=create_date('2024-03-03'))


@pytest.mark.django_db
class TestGetAccountTickerOperations:
    @pytest.fixture
    def operation_service_mock(self):
        return Mock(spec=OperationService)
    
    @pytest.fixture
    def currency_service_mock(self):
        return Mock(spec=CurrencyService)
    
    @pytest.fixture
    def profit_service_mock(self, operation_service_mock, currency_service_mock):
        return ProfitService(
            operation_service=operation_service_mock,
            currency_service=currency_service_mock
        )
        
    def test_when_no_date_end_then_returns_all_operations(self, profit_service_mock, account_default, sample_operations):
        result = profit_service_mock.get_account_ticker_operations(account_default, 'AAPL', None)
        
        assert len(result) == 3
        assert list(result) == sorted(result, key=lambda x: x.date)
        assert all(operation.account == account_default for operation in result)

    def test_when_filtered_by_date_end_then_returns_previous_operations(self, profit_service_mock, account_default, sample_operations):
        date_end = datetime(2024, 3, 1, tzinfo=timezone.utc)
        result = profit_service_mock.get_account_ticker_operations(account_default, 'AAPL', date_end)
        
        assert len(result) == 2
        assert all(operation.account == account_default and operation.date <= date_end for operation in result)

    def test_when_account_without_operations_then_returns_no_operations(self, profit_service_mock, create_account, sample_operations):
        account_without_operations = create_account()
        result = profit_service_mock.get_account_ticker_operations(account_without_operations, 'AAPL', None)
        
        assert len(result) == 0
