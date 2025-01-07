from datetime import datetime
from decimal import Decimal
from typing import Optional

from profits.models import Account, Operation
from profits.services.currency_service import is_currency_conversion
from profits.services.operation_service import get_account_ticker_operations, get_account_tickers_sold_period
from profits.services.operation_tracker import OperationTracker

def get_total(account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> Decimal:
    """
    TODO: refactor logic to base return on results from 'get_total_details'
    """
    operations = Operation.objects.filter(account=account)
    if date_start:
        operations = operations.filter(date__gte=date_start)
    if date_end:
        operations = operations.filter(date__lte=date_end)

    operations = operations.order_by('date')
    amount_total = Decimal(0)
    for sell_operation in operations:
        if is_currency_conversion(sell_operation.ticker):
            continue

        amount_total += sell_operation.amount_total

    return amount_total

def add_profit_line(sell_quantity_line: Decimal, sell: OperationTracker, buy: OperationTracker, profits: list[dict]):
    profits.append(
        {
            'sell_date': sell.date,
            'sell_quantity': sell_quantity_line,
            'sell_amount_total': sell_quantity_line * sell.price_avg,
            'sell_currency': sell.currency,
            'buy_date': buy.date,
            'buy_amount_total': sell_quantity_line * buy.price_avg,
            'buy_currency': buy.currency,
            'profit': sell_quantity_line * (sell.price_avg - buy.price_avg)
        }
    )

def add_profit_lines(sell_left: OperationTracker, buys: list[OperationTracker], buys_used_index: int, profits: list[dict]):
    while sell_left.quantity > 0 and buys_used_index < len(buys):
        if buys[buys_used_index].quantity > sell_left.quantity:
            sell_quantity_line = sell_left.quantity
            sell_left.quantity = Decimal(0)
            buys[buys_used_index].quantity -= sell_quantity_line

            add_profit_line(sell_quantity_line, sell_left, buys[buys_used_index], profits)
        else:
            sell_quantity_line = buys[buys_used_index].quantity
            sell_left.quantity -= sell_quantity_line
            buys[buys_used_index].quantity = Decimal(0)

            add_profit_line(sell_quantity_line, sell_left, buys[buys_used_index], profits)
            buys_used_index += 1
    
    if sell_left.quantity > 0:
        raise ValueError(f'On date {sell_left.date} there are {sell_left.quantity} stocks left to sell without corresponding buys.')

def create_operation_tracker(ticker_operation: Operation) -> OperationTracker:
    return OperationTracker(
        date= ticker_operation.date,
        quantity= ticker_operation.quantity,
        currency= ticker_operation.currency.iso_code,
        price_avg= ticker_operation.amount_total / ticker_operation.quantity
    )

def get_total_details_ticker(ticker_operations: list[Operation]) -> list[dict]:
    buys = []
    profits = []
    buys_used_index = 0
    
    for ticker_operation in ticker_operations:
        operation_tracker= create_operation_tracker(ticker_operation)
        if ticker_operation.type == 'BUY':
            buys.append(operation_tracker)
        else:
            try:
                add_profit_lines(operation_tracker, buys, buys_used_index, profits)
            except ValueError as e:
                raise ValueError(f'For ticker {ticker_operation.ticker} there is error: {e}') from e

    return profits

def get_total_details(account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> list[dict]:
    
    account_tickers_sold = get_account_tickers_sold_period(account, date_start, date_end)
    tickers_profit = []
    for ticker_sold in account_tickers_sold:
        if is_currency_conversion(ticker_sold):
            continue

        ticker_operations= get_account_ticker_operations(account, ticker_sold, date_end)
        
        ticker_profits = get_total_details_ticker(ticker_operations)

        tickers_profit.append(
            {
                'ticker': ticker_sold,
                'profit_detail': ticker_profits
            }
        )
    
    return tickers_profit


