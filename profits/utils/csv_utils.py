import csv
from datetime import datetime
from typing import Optional

from django.http import HttpResponse

from profits.services.profit_service import ProfitDetails
from profits.utils import datetime_utils

TOTAL_DETAILS_HEADERS_CSV = [
        'Ticker', 
        'Buy Date', 
        'Buy Amount Total', 
        'Buy Currency', 
        'Sell Date', 
        'Sell Quantity', 
        'Sell Amount Total', 
        'Sell Currency', 
        'Profit',
        'Currency Exchange',
        'Buy Exchange',
        'Buy Amount Total Exchange',
        'Sell Exchange',
        'Sell Amount Total Exchange',
        'Profit Exchange'

    ]
def generate_total_details_csv(
    tickers_profit: list[ProfitDetails],
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
        ticker = ticker_profit.get('ticker')
        profit_details = ticker_profit.get('profit_details', [])
        for profit_detail in profit_details:
            writer.writerow([
                ticker,
                profit_detail.buy_date, 
                profit_detail.buy_amount_total, 
                profit_detail.buy_currency, 
                profit_detail.sell_date, 
                profit_detail.sell_quantity, 
                profit_detail.sell_amount_total, 
                profit_detail.sell_currency, 
                profit_detail.profit, 
                profit_detail.currency_exchange,
                profit_detail.buy_exchange, 
                profit_detail.buy_amount_total_exchange, 
                profit_detail.sell_exchange, 
                profit_detail.sell_amount_total_exchange,
                profit_detail.profit_exchange
            ])

    return response
    
