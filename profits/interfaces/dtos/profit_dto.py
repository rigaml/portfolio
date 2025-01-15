from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class ProfitDTO:
    sell_date: datetime
    sell_quantity: Decimal
    sell_amount_total: Decimal
    sell_currency: str
    buy_date: datetime
    buy_amount_total: Decimal
    buy_currency: str
    profit: Decimal