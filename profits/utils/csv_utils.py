import csv
from datetime import datetime
from typing import Any

from django.http import HttpResponse

from profits.utils import datetime_utils

TOTAL_DETAILS_HEADERS_CSV = [
        'Ticker', 'Sell Date', 'Sell Quantity', 'Sell Amount Total', 'Sell Currency', 'Buy Date', 'Buy Amount Total', 'Buy Currency', 'Profit'
    ]
def generate_total_details_csv(
    tickers_profit: list[dict[str, Any]],
    account_id: int,
    date_start: datetime,
    date_end: datetime
) -> HttpResponse:

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        f'attachment; filename="totals-account-{account_id}-from-{datetime_utils.to_filename(date_start)}-to-{datetime_utils.to_filename(date_end)}.csv"'

    writer = csv.writer(response)
    writer.writerow(TOTAL_DETAILS_HEADERS_CSV)
    for ticker in tickers_profit:
        writer.writerow([
            ticker['ticker'],
            ticker['profit_detail'][0]['sell_date'], 
            ticker['profit_detail'][0]['sell_quantity'], 
            ticker['profit_detail'][0]['sell_amount_total'], 
            ticker['profit_detail'][0]['sell_currency'], 
            ticker['profit_detail'][0]['buy_date'], 
            ticker['profit_detail'][0]['buy_amount_total'], 
            ticker['profit_detail'][0]['buy_currency'], 
            ticker['profit_detail'][0]['profit'], 
        ])

    return response
    
