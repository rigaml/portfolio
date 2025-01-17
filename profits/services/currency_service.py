from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional

from profits.services.exceptions import CurrencyConversionException, CurrencyExchangeNotFoundException
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
        These are values found in the operation input data, add more if necessary.
        """

        return ticker.upper() in ('USDGBP', 'USDEUR', 'GBPUSD', 'GBPEUR', 'EURUSD', 'EURGBP')

    def get_currency_exchange(self, origin_currency_code: str, target_currency_code: str, date_request: datetime) -> Decimal:
        """
        Gets exchange rate between 2 given currencies and date.
        If there is no exchange for the given date tries to find exchange for a previous date, decreasing the date.day by one.
        """
        if origin_currency_code == target_currency_code:
            return Decimal(1)

        currency_pair_key= f"{origin_currency_code}-{target_currency_code}"
        currency_pair_exchanges= self.currencies_exchanges_cache.get(currency_pair_key, None)
        if not currency_pair_exchanges:
            currency_pair_exchanges= self.currency_repository.get_currency_exchanges(origin_currency_code, target_currency_code, self.date_start, self.date_end)
            if not currency_pair_exchanges:
                raise CurrencyExchangeNotFoundException(
                    f"No exchange rates found for {origin_currency_code}-{target_currency_code} "
                    f"between {self.date_start} and {self.date_end}")

            self.currencies_exchanges_cache[currency_pair_key] = currency_pair_exchanges

        exchange_rate = None
        date_iteration= date_request.date()
        first_date_key = next(iter(currency_pair_exchanges))

        while not exchange_rate and first_date_key <= date_iteration:
            exchange_rate= currency_pair_exchanges.get(date_iteration, None)
            date_iteration= date_iteration - timedelta(days=1)

        if exchange_rate:
            return exchange_rate

        raise CurrencyConversionException(f"Exchange for {currency_pair_key} could not be found for date {date_request}")
