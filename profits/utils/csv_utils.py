import csv
from datetime import datetime
from typing import Any, Optional

from django.http import HttpResponse

from profits.interfaces.dtos.profit_dto import ProfitDTO
from profits.utils import datetime_utils

TOTAL_DETAILS_HEADERS_CSV = [
        'Ticker', 'Sell Date', 'Sell Quantity', 'Sell Amount Total', 'Sell Currency', 'Buy Date', 'Buy Amount Total', 'Buy Currency', 'Profit'
    ]
def generate_total_details_csv(
    tickers_profit: list[dict[str, Any]],
    account_id: int,
    date_start: Optional[datetime],
    date_end: Optional[datetime]
) -> HttpResponse:

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        f'attachment; filename="totals-account-{account_id}-from-{datetime_utils.to_filename(date_start)}-to-{datetime_utils.to_filename(date_end)}.csv"'

    writer = csv.writer(response)
    writer.writerow(TOTAL_DETAILS_HEADERS_CSV)
    for ticker_profit in tickers_profit:
        ticker= ticker_profit['ticker']
        for profit_detail in ticker_profit['profit_detail']:
            writer.writerow([
                ticker,
                profit_detail.sell_date, 
                profit_detail.sell_quantity, 
                profit_detail.sell_amount_total, 
                profit_detail.sell_currency, 
                profit_detail.buy_date, 
                profit_detail.buy_amount_total, 
                profit_detail.buy_currency, 
                profit_detail.profit, 
            ])

    return response
    
