from decimal import Decimal
from profits.interfaces.dtos.operation_dto import OperationDTO
from profits.interfaces.dtos.profit_dto import ProfitDTO, ProfitExchangeDTO
from profits.services.profit_exchanger import ProfitExchanger


class ProfitCalculator():
    def __init__(self, profit_exchanger: ProfitExchanger):
        self.profit_exchanger = profit_exchanger

    def _calculate_profit_match(self, sell_quantity_line: Decimal, sell: OperationDTO, buy: OperationDTO, target_currency: str) -> ProfitExchangeDTO:
        """
        Calculate profit for a match between a SELL and a BUY operation.
        """
        profit = None
        if sell.currency == buy.currency:
            profit = sell_quantity_line * (sell.price_avg - buy.price_avg)

        profit_dto = ProfitDTO(
                sell_date= sell.date,
                sell_quantity= sell_quantity_line,
                sell_amount_total= sell_quantity_line * sell.price_avg,
                sell_currency= sell.currency,
                buy_date= buy.date,
                buy_amount_total= sell_quantity_line * buy.price_avg,
                buy_currency= buy.currency,
                profit= profit
        )

        return self.profit_exchanger.exchange_currencies(profit_dto, target_currency)
                    
    def _calculate_profits_sell(self, sell_operation: OperationDTO, buys: list[OperationDTO], target_currency: str) -> list[ProfitExchangeDTO]:
        """
        Calculate profits for a given SELL operation using the FIFO method.
        """
        quantity_sell = sell_operation.quantity
        profits_sell = []

        while quantity_sell > 0 and buys:
            current_buy = buys[0]

            if current_buy.quantity > quantity_sell:
                # Can use the buy to offset all sold
                quantity_line_sell = quantity_sell
                current_buy.quantity -= quantity_line_sell
                quantity_sell = Decimal(0)
            else:
                # Only part of the buy can be used for the sell
                quantity_line_sell = current_buy.quantity
                quantity_sell -= quantity_line_sell
                buys.pop(0)

            profit_dto= self._calculate_profit_match(quantity_line_sell, sell_operation, current_buy, target_currency)
            profits_sell.append(profit_dto)

        if quantity_sell > 0:
            raise ValueError(f'On date {sell_operation.date}, {quantity_sell} stocks left to sell without corresponding buys.')

        return profits_sell
    
    def calculate_ticker_profits(self, ticker_operations: list[OperationDTO], target_currency: str =  "GBP") -> list[ProfitExchangeDTO]:
        buys: list[OperationDTO] = []
        profits: list[ProfitExchangeDTO] = []
        
        for operation in ticker_operations:
            if operation.type == 'BUY':
                buys.append(operation)
            elif operation.type == 'SELL':
                profits_sell= self._calculate_profits_sell(operation, buys, target_currency)
                profits.extend(profits_sell)
            else:
                raise ValueError(f"Unexpected operation type {operation.type}")

        return profits    