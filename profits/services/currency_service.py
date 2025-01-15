from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from profits.models import CurrencyExchange
from profits.services.exceptions import CurrencyConversionException, CurrencyExchangeNotFoundException
    
class CurrencyService:
    def __init__(self, date_start: Optional[datetime], date_end: Optional[datetime]) -> None:
        self.date_start = date_start
        self.date_end = date_end
        self.currencies_exchanges_cache = {}
    
    @staticmethod
    def is_currency_conversion(ticker: str) -> bool:
        """
        Checks if the given ticker represents a currency conversion.
        """

        return ticker.upper() in ('USDGBP', 'USDEUR', 'GBPUSD', 'GBPEUR', 'EURUSD', 'EURGBP')

    @staticmethod
    def load_currency_exchanges(
            origin_currency_code: Optional[str], 
            target_currency_code: Optional[str], 
            date_start: Optional[datetime], 
            date_end: Optional[datetime]) -> dict:
        
        """
        Loads currency exchange rates from the database, filtered by the given parameters
        
        Returns a dictionary with the exchange rates, where the keys are the dates
                and the values are dictionaries with the exchange rates for that date.
                The keys of the inner dictionary are strings of the form
                "origin-target", where origin and target are the ISO codes of the
                currencies, and the values are the exchange rates.
        """
        exchanges= CurrencyExchange.objects
        if origin_currency_code:
            exchanges = exchanges.filter(origin_iso_code=origin_currency_code)
        if target_currency_code:
            exchanges = exchanges.filter(target_iso_code=target_currency_code)
        if date_start:
            exchanges = exchanges.filter(date__gte=date_start)
        if date_end:
            exchanges = exchanges.filter(date__lte=date_end)

        if not exchanges.exists():
            raise CurrencyExchangeNotFoundException(
                f"No exchange rates found for {origin_currency_code}-{target_currency_code} "
                f"between {date_start} and {date_end}")

        exchange_dict = {}
        for exchange in exchanges:
            exchange_dict[exchange.date] = exchange.rate

        return exchange_dict
    

    def get_currency_exchange(self, origin_currency_code: str, target_currency_code: str, date_request: datetime) -> Decimal:
        if origin_currency_code == target_currency_code:
            return Decimal(1)

        pair_key= f"{origin_currency_code}-{target_currency_code}"
        pair_exchanges= self.currencies_exchanges_cache.get(pair_key, None)
        if not pair_exchanges:
            self.currencies_exchanges_cache[pair_key]= self.load_currency_exchanges(origin_currency_code, target_currency_code, self.date_start, self.date_end)
            pair_exchanges = self.currencies_exchanges_cache[pair_key]

        exchange_rate = None
        date_iteration= date_request
        last_date = next(reversed(pair_exchanges))
        while not exchange_rate and date_iteration <= last_date:
            exchange_rate= pair_exchanges.get(date_iteration.date, None)
            date_iteration= date_iteration + timedelta(days=1)

        if exchange_rate:
            return exchange_rate
        
        raise CurrencyConversionException(f"Exchange for {pair_key} could not be found for date {date_request}")
