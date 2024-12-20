from datetime import datetime
from typing import Optional

from profits.models import CurrencyExchange


def load_currency_exchanges(
        origin_currency_code: Optional[str], 
        target_currency_code: Optional[str], 
        date_start: Optional[datetime], 
        date_end: Optional[datetime]) -> dict:
    
    exchanges= CurrencyExchange.objects
    if origin_currency_code:
        exchanges = exchanges.filter(origin_iso_code=origin_currency_code)
    if target_currency_code:
        exchanges = exchanges.filter(target_iso_code=target_currency_code)
    if date_start:
        exchanges = exchanges.filter(date__gte=date_start)
    if date_end:
        exchanges = exchanges.filter(date__lte=date_end)

    exchange_dict = {}
    for exchange in exchanges:
        day_exchange = exchange_dict.get(exchange.date, {})

        day_exchange[f"{exchange.origin.iso_code}-{exchange.target.iso_code}"] = exchange.rate

        exchange_dict[exchange.date] = day_exchange

    return exchange_dict
    
def is_currency_conversion(ticker: str) -> bool:
    return ticker.upper() in ('USDGBP', 'USDEUR', 'GBPUSD', 'GBPEUR', 'EURUSD', 'EURGBP')

