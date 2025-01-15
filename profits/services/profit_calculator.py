from decimal import Decimal
from profits.interfaces.dtos.operation_dto import OperationDTO
from profits.interfaces.dtos.profit_dto import ProfitDTO


class ProfitCalculator:
    def __init__(self):
        self.buys = []
        self.profits = []

    def _create_profit_dto(self, sell_quantity_line: Decimal, sell: OperationDTO, buy: OperationDTO) -> ProfitDTO:
        return ProfitDTO(
                sell_date= sell.date,
                sell_quantity= sell_quantity_line,
                sell_amount_total= sell_quantity_line * sell.price_avg,
                sell_currency= sell.currency,
                buy_date= buy.date,
                buy_amount_total= sell_quantity_line * buy.price_avg,
                buy_currency= buy.currency,
                profit= sell_quantity_line * (sell.price_avg - buy.price_avg)
        )
                    
    def _add_buy(self, buy_operation: OperationDTO):
        self.buys.append(buy_operation)

    def _calculate_profits_for_sell(self, sell_operation: OperationDTO) -> list[ProfitDTO]:
        """
        Calculate profits for a given SELL operation using the FIFO method.
        """
        sell_quantity = sell_operation.quantity
        profits = []

        while sell_quantity > 0 and self.buys:
            current_buy = self.buys[0]

            if current_buy.quantity > sell_quantity:
                # Can use the buy to offset all sold
                sell_quantity_line = sell_quantity
                current_buy.quantity -= sell_quantity_line
                sell_quantity = Decimal(0)
            else:
                # Only part of the buy can be used for the sell
                sell_quantity_line = current_buy.quantity
                sell_quantity -= sell_quantity_line
                self.buys.pop(0)

            profit_dto= self._create_profit_dto(sell_quantity_line, sell_operation, current_buy)
            profits.append(profit_dto)

        if sell_quantity > 0:
            raise ValueError(f'On date {sell_operation.date}, {sell_quantity} stocks left to sell without corresponding buys.')

        return profits
    
    def calculate_ticker_profits(self, ticker_operations: list[OperationDTO]) -> list[ProfitDTO]:
        profits = []
        
        for operation in ticker_operations:
            if operation.type == 'BUY':
                self._add_buy(operation)
            elif operation.type == 'SELL':
                profits_sell= self._calculate_profits_for_sell(operation)
                profits.extend(profits_sell)
            else:
                raise ValueError(f"Unexpected operation type {operation.type}")

        return profits    