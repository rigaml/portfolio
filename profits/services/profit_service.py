from datetime import datetime
from decimal import Decimal
from typing import Optional, TypedDict

from profits.models import Account
from profits.repositories.operation_repository import OperationRepository
from profits.services.currency_service import CurrencyService
from profits.services.profit_calculator import ProfitCalculator
from profits.interfaces.dtos.profit_dto import ProfitExchangeDTO
from profits.services.exceptions import ProfitServiceBuySellMissmatch

import logging
logger = logging.getLogger('profits.services')

class ProfitDetails(TypedDict):
    ticker: str
    profit_details: list[ProfitExchangeDTO]

class ProfitService:
    def __init__(
            self, 
            operation_repository: OperationRepository, 
            currency_service: CurrencyService,
            profit_calculator: ProfitCalculator):
        self.operation_repository = operation_repository
        self.currency_service = currency_service        
        self.profit_calculator = profit_calculator        

    def get_total(self, account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> Decimal:
        amount_total = Decimal(0)
        account_tickers_sold = self.operation_repository.get_account_tickers_sold_period(account, date_start, date_end)
        for ticker_sold in account_tickers_sold:
            if self.currency_service.is_currency_conversion(ticker_sold):
                continue

            ticker_operations= self.operation_repository.get_account_ticker_operations(account, ticker_sold, date_end)

            try:
                ticker_profits = self.profit_calculator.calculate_ticker_profits(ticker_operations)
            except ValueError as e:
                logger.exception(f'Error calculating profits for ticker {ticker_sold}')
                raise ProfitServiceBuySellMissmatch(f'For ticker {ticker_sold} there is error: {e}') from e
            
            amount_total += sum(ticker_profit.profit_exchange for ticker_profit in ticker_profits)

        return amount_total

    def get_total_details(self, account: Account, date_start: Optional[datetime], date_end: Optional[datetime]) -> list[ProfitDetails]:        
        account_tickers_sold = self.operation_repository.get_account_tickers_sold_period(account, date_start, date_end)
        tickers_profit = []
        for ticker_sold in account_tickers_sold:
            if self.currency_service.is_currency_conversion(ticker_sold):
                continue

            ticker_operations= self.operation_repository.get_account_ticker_operations(account, ticker_sold, date_end)

            try:
                ticker_profits = self.profit_calculator.calculate_ticker_profits(ticker_operations)
            except ValueError as e:
                logger.exception(f'Error calculating profits for ticker {ticker_sold}')
                raise ProfitServiceBuySellMissmatch(f'For ticker {ticker_sold} there is error: {e}') from e

            tickers_profit.append(
                {
                    'ticker': ticker_sold,
                    'profit_details': ticker_profits
                }
            )
        
        return tickers_profit


