from decimal import Decimal
from unittest.mock import Mock
import pytest

from datetime import datetime, timezone

from profits.services.profit_calculator import ProfitCalculator
from profits.interfaces.dtos.operation_dto import OperationDTO
from profits.interfaces.dtos.profit_dto import ProfitDTO


class TestCalculateTickerProfits:
    @pytest.fixture
    def mock_operation_dto(self):
        def _create_operation_dto(
                type="BUY",
                date=None, 
                quantity=Decimal('10.00'), 
                currency='GBP', 
                price_avg=Decimal('1000.00')):
            # Using "Mock(spec=OperationDTO)" so test is loosely coupled to OperationDTO implementation (future proofing)
            operation_dto = Mock(spec=OperationDTO)
            operation_dto.type = type
            operation_dto.date = date or datetime(2024, 1, 1, tzinfo=timezone.utc)
            operation_dto.quantity = quantity
            operation_dto.currency = currency
            operation_dto.price_avg = price_avg
            return operation_dto
        return _create_operation_dto   
            
    def test_when_no_operations_then_returns_empty_list(self):
        ticker_operations = []

        profit_calculator = ProfitCalculator()
        result = profit_calculator.calculate_ticker_profits(ticker_operations)
        
        assert len(result) == 0

    def test_when_sell_without_buy_then_raises_exception(self, mock_operation_dto):
        ticker_operations = [mock_operation_dto(type='SELL')]

        profit_calculator = ProfitCalculator()
        with pytest.raises(ValueError) as e:
            profit_calculator.calculate_ticker_profits(ticker_operations)

    def test_when_sell_quantity_bigger_than_buy_then_raises_exception(self, mock_operation_dto):
        ticker_operations = [
            mock_operation_dto(type='BUY', quantity=Decimal('10.00')),
            mock_operation_dto(type='SELL', quantity=Decimal('11.00'))
        ]

        profit_calculator = ProfitCalculator()
        with pytest.raises(ValueError) as e:
            profit_calculator.calculate_ticker_profits(ticker_operations)

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
            sell_date=datetime(2024, 2, 1, tzinfo=timezone.utc), sell_quantity=Decimal(10), sell_amount_total=Decimal(1100), sell_currency='GBP',
            buy_date=datetime(2024, 1, 1, tzinfo=timezone.utc), buy_amount_total=Decimal(1000), buy_currency='GBP', profit=Decimal(100)),
         ProfitDTO(
            sell_date=datetime(2024, 2, 15, tzinfo=timezone.utc), sell_quantity=Decimal(10), sell_amount_total=Decimal(1200), sell_currency='GBP',
            buy_date=datetime(2024, 1, 1, tzinfo=timezone.utc), buy_amount_total=Decimal(1000), buy_currency='GBP', profit=Decimal(200))]),
    ])
    def test_when_sell_with_matching_buy_then_returns_profit(self, mock_operation_dto, operations, expected_profits):
        ticker_operations = []
        for operation in operations:
            ticker_operations.append(
                mock_operation_dto(
                    type= operation['type'], 
                    date= operation['date'], 
                    quantity= Decimal(str(operation['quantity'])),
                    currency= 'GBP',
                    price_avg= Decimal(operation['price_avg'])
                )
            ) 

        profit_calculator = ProfitCalculator()
        result = profit_calculator.calculate_ticker_profits(ticker_operations)

        assert result == expected_profits