from datetime import datetime
from decimal import Decimal
from typing import Optional

from profits.models import Account
from profits.services.currency_service import CurrencyService
from profits.services.operation_service import OperationService
from profits.services.profit_calculator import ProfitCalculator
from profits.services.profit_dto import ProfitDTO
from profits.services.exceptions import ProfitServiceBuySellMissmatch

class ProfitService:
    def __init__(
            self, 
            operation_service: OperationService, 
            currency_service: CurrencyService,
            profit_calculator: ProfitCalculator):
        self.operation_service = operation_service
        self.currency_service = currency_service        
        self.profit_calculator = profit_calculator        

    def get_total(self, account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> Decimal:
        amount_total = Decimal(0)
        account_tickers_sold = self.operation_service.get_account_tickers_sold_period(account, date_start, date_end)
        for ticker_sold in account_tickers_sold:
            if self.currency_service.is_currency_conversion(ticker_sold):
                continue

            ticker_operations= self.operation_service.get_account_ticker_operations(account, ticker_sold, date_end)

            try:
                ticker_profits = self.profit_calculator.calculate_ticker_profits(ticker_operations)
            except ValueError as e:
                raise ProfitServiceBuySellMissmatch(f'For ticker {ticker_sold} there is error: {e}') from e
            
            amount_total += sum(ticker_profit.profit for ticker_profit in ticker_profits)

        return amount_total

    def get_total_details(self, account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> list[dict[str, str | ProfitDTO]]:
        
        account_tickers_sold = self.operation_service.get_account_tickers_sold_period(account, date_start, date_end)
        tickers_profit = []
        for ticker_sold in account_tickers_sold:
            if self.currency_service.is_currency_conversion(ticker_sold):
                continue

            ticker_operations= self.operation_service.get_account_ticker_operations(account, ticker_sold, date_end)

            try:
                ticker_profits = self.profit_calculator.calculate_ticker_profits(ticker_operations)
            except ValueError as e:
                raise ProfitServiceBuySellMissmatch(f'For ticker {ticker_sold} there is error: {e}') from e

            tickers_profit.append(
                {
                    'ticker': ticker_sold,
                    'profit_detail': ticker_profits
                }
            )
        
        return tickers_profit


