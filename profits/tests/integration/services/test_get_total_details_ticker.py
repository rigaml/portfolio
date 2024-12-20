from decimal import Decimal
import pytest

from datetime import datetime, timezone

from profits.tests.conftest import create_date
from profits.services.profit_service import get_total_details_ticker


@pytest.mark.django_db
class TestGetTotalDetailsTicker:
    def test_when_no_operations_then_returns_empty_list(self):
        ticker_operations = []

        result = get_total_details_ticker(ticker_operations)
        
        assert len(result) == 0

    def test_when_sell_without_buy_then_raises_exception(self, create_operation):
        ticker_operations = [create_operation(type='SELL')]

        with pytest.raises(Exception) as e:
            get_total_details_ticker(ticker_operations)

    def test_when_sell_quantity_bigger_than_buy_then_raises_exception(self, create_operation, create_date):
        ticker_operations = [
            create_operation(type='BUY', date=create_date('2024-01-01'), quantity=Decimal('10.00')), 
            create_operation(type='SELL', date=create_date('2024-02-01'), quantity=Decimal('11.00'))]

        with pytest.raises(Exception) as e:
            get_total_details_ticker(ticker_operations)

    def test_when_sell_with_matching_buy_then_returns_profit(self, create_operation, create_date):
        ticker_operations = [
            create_operation(type='BUY', date=create_date('2024-01-01')), 
            create_operation(type='SELL', date=create_date('2024-02-01'), amount_total=Decimal('11000.00'))]

        result = get_total_details_ticker(ticker_operations)
    
        assert len(result) == 1
        assert result[0]['sell_date'] == datetime(2024, 2, 1, tzinfo=timezone.utc)
        assert result[0]['sell_quantity'] == Decimal('10')
        assert result[0]['sell_amount_total'] == Decimal('11000.00')
        assert result[0]['sell_currency'] == 'GBP'
        assert result[0]['buy_date'] == datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert result[0]['buy_amount_total'] == Decimal('10000.00')
        assert result[0]['buy_currency'] == 'GBP'
        assert result[0]['profit'] == Decimal('1000.00')
