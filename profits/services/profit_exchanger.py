import dataclasses
from profits.interfaces.dtos.profit_dto import ProfitDTO, ProfitExchangeDTO
from profits.services.currency_service import CurrencyService


class ProfitExchanger:
    def __init__(self, currency_service: CurrencyService):
        self.currency_service = currency_service

    def exchange_currencies(self, profit_dto: ProfitDTO, target_currency: str) -> ProfitExchangeDTO:
        buy_exchange= self.currency_service.get_currency_exchange(profit_dto.buy_currency, target_currency, profit_dto.buy_date)
        buy_amount_total_exchange = profit_dto.buy_amount_total * buy_exchange

        sell_exchange= self.currency_service.get_currency_exchange(profit_dto.sell_currency, target_currency, profit_dto.sell_date)
        sell_amount_total_exchange = profit_dto.sell_amount_total * sell_exchange
        
        profit_exchange_dto= ProfitExchangeDTO(
            **dataclasses.asdict(profit_dto),
            currency_exchange=target_currency,
            buy_exchange= buy_exchange,
            buy_amount_total_exchange= buy_amount_total_exchange,
            sell_exchange= sell_exchange,
            sell_amount_total_exchange= sell_amount_total_exchange,
            profit_exchange = sell_amount_total_exchange - buy_amount_total_exchange
        )

        return profit_exchange_dto