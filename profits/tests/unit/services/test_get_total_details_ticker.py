from decimal import Decimal
from unittest.mock import Mock
import pytest

from datetime import datetime, timezone

from profits.models import Operation
from profits.services.exceptions import ProfitServiceBuySellMissmatch
from profits.services.profit_service import ProfitService
from profits.services.currency_service import CurrencyService
from profits.services.operation_service import OperationService
from profits.services.profit_dto import ProfitDTO


class TestGetTotalDetailsTicker:
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
    
    @pytest.fixture
    def mock_operation(self):
        def _create_operation(
                type='SELL', date=None, quantity=Decimal('10.00'), 
                amount_total=Decimal('1000.00'), currency='GBP', ticker='AAPL'):
            operation = Mock(spec=Operation)
            operation.type = type
            operation.date = date or datetime(2024, 1, 1, tzinfo=timezone.utc)
            operation.quantity = quantity
            operation.amount_total = amount_total
            operation.currency.iso_code = currency
            operation.ticker = ticker
            return operation
        return _create_operation    
        
    def test_when_no_operations_then_returns_empty_list(self, profit_service_mock):
        ticker_operations = []

        result = profit_service_mock.get_total_details_ticker(ticker_operations)
        
        assert len(result) == 0

    def test_when_sell_without_buy_then_raises_exception(self, profit_service_mock, mock_operation):
        ticker_operations = [mock_operation(type='SELL')]

        with pytest.raises(ProfitServiceBuySellMissmatch) as e:
            profit_service_mock.get_total_details_ticker(ticker_operations)

    def test_when_sell_quantity_bigger_than_buy_then_raises_exception(self, profit_service_mock, mock_operation):
        ticker_operations = [
            mock_operation(type='BUY'),
            mock_operation(type='SELL', quantity=Decimal('11.00'))
        ]

        with pytest.raises(ProfitServiceBuySellMissmatch) as e:
            profit_service_mock.get_total_details_ticker(ticker_operations)

    @pytest.mark.parametrize("operations, expected_profits", [
        # Case 1: Corresponding buy and sell
        ([{'type': 'BUY', 'date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 100},
        {'type': 'SELL', 'date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 110}],
        [ProfitDTO(
            sell_date=datetime(2024, 2, 1, tzinfo=timezone.utc), sell_quantity=Decimal(10), sell_amount_total=Decimal(1100), sell_currency='GBP',
            buy_date=datetime(2024, 1, 1, tzinfo=timezone.utc), buy_amount_total=Decimal(1000), buy_currency='GBP', profit=Decimal(100))]),

        # Case 2: Multiple buys, one sell (FIFO)
        ([{'type': 'BUY', 'date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'quantity': 5, 'price_avg': 100},
        {'type': 'BUY', 'date': datetime(2024, 1, 15, tzinfo=timezone.utc), 'quantity': 5, 'price_avg': 95},
        {'type': 'SELL', 'date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 110}],
        [ProfitDTO(
            sell_date=datetime(2024, 2, 1, tzinfo=timezone.utc), sell_quantity=Decimal(5), sell_amount_total=Decimal(550), sell_currency='GBP',
            buy_date=datetime(2024, 1, 1, tzinfo=timezone.utc), buy_amount_total=Decimal(500), buy_currency='GBP', profit=Decimal(50)),
        ProfitDTO(
            sell_date=datetime(2024, 2, 1, tzinfo=timezone.utc), sell_quantity=Decimal(5), sell_amount_total=Decimal(550), sell_currency='GBP',
            buy_date=datetime(2024, 1, 15, tzinfo=timezone.utc), buy_amount_total=Decimal(475), buy_currency='GBP', profit=Decimal(75))]),

        # Case 3: One buy, multiple sells
        ([{'type': 'BUY', 'date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'quantity': 20, 'price_avg': 100},
        {'type': 'SELL', 'date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 110},
        {'type': 'SELL', 'date': datetime(2024, 2, 15, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 120}],
        [ProfitDTO(
            sell_date=datetime(2024, 2, 1, tzinfo=timezone.utc), sell_quantity=10, sell_amount_total=1100, sell_currency='GBP',
            buy_date=datetime(2024, 1, 1, tzinfo=timezone.utc), buy_amount_total=1000, buy_currency='GBP', profit=100),
        ProfitDTO(
            sell_date=datetime(2024, 2, 15, tzinfo=timezone.utc), sell_quantity=10, sell_amount_total=1200, sell_currency='GBP',
            buy_date=datetime(2024, 1, 1, tzinfo=timezone.utc), buy_amount_total=1000, buy_currency='GBP', profit=200)]),
    ])
    def test_when_sell_with_matching_buy_then_returns_profit(self, profit_service_mock, mock_operation, operations, expected_profits):
        ticker_operations = []
        for operation in operations:
            ticker_operations.append(
                mock_operation(
                    type=operation['type'],
                    date= operation['date'], 
                    quantity= Decimal(str(operation['quantity'])),
                    amount_total= Decimal(str(operation['quantity'] * operation['price_avg'])),
                    currency= 'GBP')
            ) 

        result = profit_service_mock.get_total_details_ticker(ticker_operations)

        assert result == expected_profits