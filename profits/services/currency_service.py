from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from profits.services.exceptions import CurrencyConversionException
from profits.repositories.currency_repository import CurrencyRepository

class CurrencyService:
    def __init__(self, currency_repository: CurrencyRepository, date_start: Optional[datetime], date_end: Optional[datetime]) -> None:
        self.currency_repository = currency_repository
        self.date_start = date_start
        self.date_end = date_end
        self.currencies_exchanges_cache = {}
    
    @staticmethod
    def is_currency_conversion(ticker: str) -> bool:
        """
        Checks if the given ticker represents a currency conversion.
        """

        return ticker.upper() in ('USDGBP', 'USDEUR', 'GBPUSD', 'GBPEUR', 'EURUSD', 'EURGBP')

    def get_currency_exchange(self, origin_currency_code: str, target_currency_code: str, date_request: datetime) -> Decimal:
        """
        Gets exchange rate between 2 given currencies and date.
        If there is no exchange for the given date tries to find exchange for a previous date, decreasing the date.day by one.
        """
        if origin_currency_code == target_currency_code:
            return Decimal(1)

        pair_key= f"{origin_currency_code}-{target_currency_code}"
        pair_exchanges= self.currencies_exchanges_cache.get(pair_key, None)
        if not pair_exchanges:
            self.currencies_exchanges_cache[pair_key]= self.currency_repository.get_currency_exchanges(origin_currency_code, target_currency_code, self.date_start, self.date_end)
            pair_exchanges = self.currencies_exchanges_cache[pair_key]

        exchange_rate = None
        date_iteration= date_request
        first_date = next(iter(pair_exchanges))
        while not exchange_rate and first_date <= date_iteration:
            exchange_rate= pair_exchanges.get(date_iteration.date, None)
            date_iteration= date_iteration - timedelta(days=1)

        if exchange_rate:
            return exchange_rate
        
        raise CurrencyConversionException(f"Exchange for {pair_key} could not be found for date {date_request}")
