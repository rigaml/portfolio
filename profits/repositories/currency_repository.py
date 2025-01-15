from datetime import datetime
from typing import Optional

from profits.models import CurrencyExchange
from profits.services.exceptions import CurrencyExchangeNotFoundException
    
class CurrencyRepository:
    @staticmethod
    def get_currency_exchanges(
            origin_currency_code: Optional[str], 
            target_currency_code: Optional[str], 
            date_start: Optional[datetime], 
            date_end: Optional[datetime]) -> dict:
        
        """
        Loads currency exchange rates from the database, filtered by the given parameters and in ascending order by date.
        
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

        exchanges = exchanges.order_by('date')

        if not exchanges.exists():
            raise CurrencyExchangeNotFoundException(
                f"No exchange rates found for {origin_currency_code}-{target_currency_code} "
                f"between {date_start} and {date_end}")

        exchange_dict = {}
        for exchange in exchanges:
            exchange_dict[exchange.date] = exchange.rate

        return exchange_dict