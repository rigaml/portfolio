from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock
import pytest

from profits.services.operation_dto import OperationDTO
from profits.services.profit_calculator import ProfitCalculator
from profits.services.profit_dto import ProfitDTO
from profits.services.profit_service import ProfitService
from profits.services.currency_service import CurrencyService
from profits.services.operation_service import OperationService

class TestGetTotalDetails:
    @pytest.fixture
    def operation_service_mock(self):
        return Mock(spec=OperationService)
    
    @pytest.fixture
    def currency_service_mock(self):
        return Mock(spec=CurrencyService)
    
    @pytest.fixture
    def profit_calculator_mock(self):
        return Mock(spec=ProfitCalculator)    
    
    @pytest.fixture
    def profit_service_mock(self, operation_service_mock, currency_service_mock, profit_calculator_mock):
        return ProfitService(
            operation_service=operation_service_mock,
            currency_service=currency_service_mock,
            profit_calculator= profit_calculator_mock
        )
    
    def test_profit_service_get_total_details(
            self, 
            profit_service_mock, 
            operation_service_mock, 
            currency_service_mock,
            profit_calculator_mock):
        account = Mock()
        operation_service_mock.get_account_tickers_sold_period.return_value = ['AAPL']
        operation_service_mock.get_account_ticker_operations.return_value = [
            OperationDTO(type='BUY', date=datetime(2024, 1, 1), quantity=Decimal('10'), currency='USD', price_avg=Decimal('100')),
            OperationDTO(type='SELL', date=datetime(2024, 2, 1), quantity=Decimal('10'), currency='USD', price_avg=Decimal('120'))
        ]
        currency_service_mock.is_currency_conversion.return_value = False
        profit_calculator_mock.calculate_ticker_profits.return_value = [
            ProfitDTO(
            sell_date=datetime(2024, 2, 15, tzinfo=timezone.utc), sell_quantity=Decimal(10), sell_amount_total=Decimal(1200), sell_currency='GBP',
            buy_date=datetime(2024, 1, 1, tzinfo=timezone.utc), buy_amount_total=Decimal(1000), buy_currency='GBP', profit=Decimal(200))]

        result = profit_service_mock.get_total_details(account, None, None)

        assert len(result) == 1
        assert result[0]['ticker'] == 'AAPL'
        assert len(result[0]['profit_detail']) == 1
        assert result[0]['profit_detail'][0].profit == Decimal('200')