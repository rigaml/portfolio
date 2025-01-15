from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class OperationDTO:
    type: str
    date: datetime
    quantity: Decimal
    currency: str
    price_avg: Decimal