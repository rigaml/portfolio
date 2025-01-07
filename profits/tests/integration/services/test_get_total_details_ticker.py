from decimal import Decimal
from locale import currency
import pytest

from datetime import datetime, timezone

from profits.models import Operation
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

        with pytest.raises(ValueError) as e:
            get_total_details_ticker(ticker_operations)

    def test_when_sell_quantity_bigger_than_buy_then_raises_exception(self, create_operation, create_date):
        ticker_operations = [
            create_operation(type='BUY', date=create_date('2024-01-01'), quantity=Decimal('10.00')), 
            create_operation(type='SELL', date=create_date('2024-02-01'), quantity=Decimal('11.00'))]

        with pytest.raises(ValueError) as e:
            get_total_details_ticker(ticker_operations)

    @pytest.mark.parametrize("buys, sells, expected_profits", [
        # Case 1: Corresponding buy and sell
        ([{'date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 100}],
         [{'date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 110}],
         [{'sell_date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'sell_quantity': 10, 'sell_amount_total': 1100, 'sell_currency': 'GBP',
           'buy_date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'buy_amount_total': 1000, 'buy_currency': 'GBP', 'profit': 100}]),

        # Case 2: Multiple buys, one sell (FIFO)
        ([{'date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'quantity': 5, 'price_avg': 100},
          {'date': datetime(2024, 1, 15, tzinfo=timezone.utc), 'quantity': 5, 'price_avg': 95}],
         [{'date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 110}],
         [{'sell_date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'sell_quantity': 5, 'sell_amount_total': 550, 'sell_currency': 'GBP',
           'buy_date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'buy_amount_total': 500, 'buy_currency': 'GBP', 'profit': 50},
           {'sell_date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'sell_quantity': 5, 'sell_amount_total': 550, 'sell_currency': 'GBP',
           'buy_date': datetime(2024, 1, 15, tzinfo=timezone.utc), 'buy_amount_total': 475, 'buy_currency': 'GBP', 'profit': 75}]),

        # Case 3: One buy, multiple sells
        ([{'date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'quantity': 20, 'price_avg': 100}],
         [{'date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 110},
          {'date': datetime(2024, 2, 15, tzinfo=timezone.utc), 'quantity': 10, 'price_avg': 120}],
         [{'sell_date': datetime(2024, 2, 1, tzinfo=timezone.utc), 'sell_quantity': 10, 'sell_amount_total': 1100, 'sell_currency': 'GBP',
           'buy_date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'buy_amount_total': 1000, 'buy_currency': 'GBP', 'profit': 100},
           {'sell_date': datetime(2024, 2, 15, tzinfo=timezone.utc), 'sell_quantity': 10, 'sell_amount_total': 1200, 'sell_currency': 'GBP',
           'buy_date': datetime(2024, 1, 1, tzinfo=timezone.utc), 'buy_amount_total': 1000, 'buy_currency': 'GBP', 'profit': 200}]),
    ])
    def test_when_sell_with_matching_buy_then_returns_profit(self, currency_gbp, buys, sells, expected_profits):
        ticker_operations = []
        for buy in buys:
            ticker_operations.append(
                Operation(
                    type='BUY',
                    date=buy['date'], 
                    quantity=buy['quantity'], 
                    amount_total=buy['quantity'] * buy['price_avg'],
                    currency=currency_gbp)) 

        for sell in sells:
            ticker_operations.append(
                Operation(
                    type='SELL',
                    date=sell['date'], 
                    quantity=sell['quantity'], 
                    amount_total=sell['quantity'] * sell['price_avg'],
                    currency=currency_gbp))                     

        result = get_total_details_ticker(ticker_operations)

        assert result == expected_profits