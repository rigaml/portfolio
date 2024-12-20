from datetime import datetime
from decimal import Decimal
from typing import Optional

from profits.models import Account, CurrencyExchange, Operation

def load_currency_exchanges(date_start: Optional[datetime], date_end: Optional[datetime]) -> None:
    exchanges= CurrencyExchange.objects
    if date_start:
        exchanges = exchanges.filter(date__gte=date_start)
    if date_end:
        exchanges = exchanges.filter(date__lte=date_end)

    exchange_dict = {}
    for exchange in exchanges:
        day_exchange = exchange_dict.get(exchange.date, {})

        day_exchange[f"{exchange.origin.iso_code}-{exchange.target.iso_code}"] = exchange.rate

        exchange_dict[exchange.date] = day_exchange
    
def is_currency_conversion(ticker: str) -> bool:
    return ticker.upper() in ('USDGBP', 'USDEUR', 'GBPUSD', 'GBPEUR', 'EURUSD', 'EURGBP')

def get_total(account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> Decimal:
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

def get_account_tickers_sold_period(account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> list[str]:
    operations = Operation.objects.filter(account=account)
    if date_start:
        operations = operations.filter(date__gte=date_start)
    if date_end:
        operations = operations.filter(date__lte=date_end)

    operations = operations.filter(type='SELL')

    operations = operations.values_list('ticker', flat=True).distinct()

    return list(operations)

def get_account_ticker_operations(account: Account, ticker_sold: str, date_end: Optional[datetime]) -> list[Operation]:
    operations = Operation.objects.filter(account=account).filter(ticker=ticker_sold)
    if date_end:
        operations = operations.filter(date__lte=date_end)

    operations = operations.order_by('date', 'type')  # Order also by type so 'BUY' comes before 'SELL'

    return list(operations)

def add_profit_line(sell_quantity_line: int, sell: dict, buy: dict, profits: list[dict]):
    profits.append(
        {
            'sell_date': sell['date'],
            'sell_quantity': sell_quantity_line,
            'sell_amount_total': sell_quantity_line * sell['price_avg'],
            'sell_currency': sell['currency'],
            'buy_date': buy['date'],
            'buy_amount_total': sell_quantity_line * buy['price_avg'],
            'buy_currency': buy['currency'],
            'profit': sell_quantity_line * (sell['price_avg'] - buy['price_avg'])
        }
    )

def add_profit_lines(sell_left: dict, buys: list[dict], buys_used_index: int, profits: list[dict]):
    while sell_left['quantity'] > 0 and buys_used_index < len(buys):
        if buys[buys_used_index]['quantity'] > sell_left['quantity']:
            sell_quantity_line = sell_left['quantity']
            sell_left['quantity'] = 0
            buys[buys_used_index]['quantity'] -= sell_quantity_line

            add_profit_line(sell_quantity_line, sell_left, buys[buys_used_index], profits)
        else:
            sell_quantity_line = buys[buys_used_index]['quantity']
            sell_left['quantity'] -= sell_quantity_line
            buys[buys_used_index]['quantity'] = 0

            add_profit_line(sell_quantity_line, sell_left, buys[buys_used_index], profits)
            buys_used_index += 1
    
    if sell_left['quantity'] > 0:
        raise ValueError(f'There are {sell_left["quantity"]} sells left on date {sell_left["date"]} but no buys.')

def create_operation_tracker(ticker_operation: Operation) -> dict:
    return {
        'date': ticker_operation.date,
        'quantity': ticker_operation.quantity,
        'currency': ticker_operation.currency.iso_code,
        'price_avg': ticker_operation.amount_total / ticker_operation.quantity
    }

def get_total_details_ticker(ticker_operations: list[Operation]) -> list[dict]:
    buys = []
    profits = []
    buys_used_index = 0
    
    for ticker_operation in ticker_operations:
        ticker_counter= create_operation_tracker(ticker_operation)
        if ticker_operation.type == 'BUY':
            buys.append(ticker_counter)
        else:
            try:
                add_profit_lines(ticker_counter, buys, buys_used_index, profits)
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


