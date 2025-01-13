from datetime import datetime
from typing import Optional
from profits.models import Account, Operation


class OperationService:
    def get_account_tickers_sold_period(self, account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> list[str]:
        """
        Returns the list of tickers that were sold within the given time period for the given account.
        """
        operations = Operation.objects.filter(account=account)
        if date_start:
            operations = operations.filter(date__gte=date_start)
        if date_end:
            operations = operations.filter(date__lte=date_end)

        operations = operations.filter(type='SELL')

        operations = operations.values_list('ticker', flat=True).distinct()

        return list(operations)

    def get_account_ticker_operations(self, account: Account, ticker_sold: str, date_end: Optional[datetime]) -> list[Operation]:
        operations = Operation.objects.filter(account=account).filter(ticker=ticker_sold)
        if date_end:
            operations = operations.filter(date__lte=date_end)

        operations = operations.order_by('date', 'type')  # Order by type so 'BUY' come before 'SELL' and no error if on same date

        return list(operations)

