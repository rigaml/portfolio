from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class OperationTracker:
    date: datetime
    quantity: Decimal
    currency: str
    price_avg: Decimal