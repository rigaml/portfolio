from datetime import datetime
from decimal import Decimal
from typing import List, Optional

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
        if is_currency_conversion(sell_operation):
            continue

        amount_total += sell_operation.amount_total

    return amount_total

def get_account_tickers_sold_period(account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> List[str]:
    operations = Operation.objects.filter(account=account)
    if date_start:
        operations = operations.filter(date__gte=date_start)
    if date_end:
        operations = operations.filter(date__lte=date_end)

    operations = operations.filter(type='SELL')

    operations = operations.values_list('ticker', flat=True).distinct()

    return list(operations)

def get_account_ticker_operations(account: Account, date_end: Optional[datetime]) -> List[Operation]:
    operations = Operation.objects.filter(account=account)
    if date_end:
        operations = operations.filter(date__lte=date_end)

    operations = operations.order_by('date')

    return list(operations)


def get_total_details(account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> List[Operation]:
    account_tickers_sold = get_account_tickers_sold_period(account, date_start, date_end)
    for operation_sell in account_tickers_sold:
        if is_currency_conversion(operation_sell):
            continue

        ticker_operations= get_account_ticker_operations(account, date_end)

        ticker_profits = []
        for ticker_operation in ticker_operations:
            if ticker_operation.type == 'BUY':
                ticker_profits.append(
                    {
                        'date': ticker_operation.date,
                        'type': ticker_operation.type,
                        'quantity': ticker_operation.quantity,
                        'amount_total': ticker_operation.amount_total
                    }
                )
            else:
                ticker_profits.append(
                    {
                        'date': ticker_operation.date,
                        'type': ticker_operation.type,
                        'quantity': ticker_operation.quantity,
                        'amount_total': ticker_operation.amount_total,
                        'profit': ticker_operation.amount_total - ticker_profits[0].amount_total
                    }
                )

    return ticker_profits