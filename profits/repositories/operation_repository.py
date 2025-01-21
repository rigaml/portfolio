from datetime import datetime
from typing import Optional
from profits.interfaces.dtos.operation_dto import OperationDTO
from profits.models import Account, Operation


class OperationRepository:
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

        tickers = operations.values_list('ticker', flat=True).distinct()

        return list(tickers)

    def get_account_ticker_operations(self, account: Account, ticker: str, date_end: Optional[datetime]) -> list[OperationDTO]:
        """
        Obtains operatios for the account for a ticker before given date.
        To calculate profits want all the previous operations as need to know at what price ticker was bought.
        Returning `OperationDTO` to remove dependency from the database.
        """
        operations = Operation.objects.filter(account=account).filter(ticker=ticker)
        if date_end:
            operations = operations.filter(date__lte=date_end)

        operations = operations.order_by('date', 'type')  # Order by type so 'BUY' come before 'SELL' and no error if on same date

        return [operation.to_dto() for operation in operations]

