from datetime import datetime, timezone
from decimal import Decimal
from profits.interfaces.dtos.profit_dto import ProfitDTO
from profits.utils.csv_utils import generate_total_details_csv, TOTAL_DETAILS_HEADERS_CSV


def test_generate_total_details_csv_when_no_detail_returns_empty_csv():
    total_details = []

    response = generate_total_details_csv(
        total_details,
        1,
        datetime(2023, 1, 1, tzinfo=timezone.utc),
        datetime(2023, 12, 31, tzinfo=timezone.utc)
    )
    
    assert response['Content-Type'] == 'text/csv'
    assert 'attachment; filename=' in response['Content-Disposition']
    
    content = response.content.decode('utf-8')
    lines = content.strip().split('\n')
    assert len(lines) == 1  # Header only
    
    header = lines[0].split(',')
    header[len(header) - 1] = header[len(header) - 1].strip()  # removes '\r' if added at the end of the line
    expected_headers = TOTAL_DETAILS_HEADERS_CSV
    assert header == expected_headers


def test_generate_total_details_csv_when_one_detail_returns_correct_csv():
    total_details = [{
            'ticker': 'AAPL',
            'profit_details': [
                ProfitDTO(
                    sell_date= datetime(2023, 6, 1, tzinfo=timezone.utc),
                    sell_quantity= Decimal(100),
                    sell_amount_total= Decimal(15000),
                    sell_currency= 'USD',
                    buy_date= datetime(2023, 1, 15, tzinfo=timezone.utc),
                    buy_amount_total= Decimal(10000),
                    buy_currency= 'USD',
                    profit= Decimal(5000)
                )
            ]
    }]
    
    response = generate_total_details_csv(
        total_details,
        1,
        datetime(2023, 1, 1, tzinfo=timezone.utc),
        datetime(2023, 12, 31, tzinfo=timezone.utc)
    )
    
    assert response['Content-Type'] == 'text/csv'
    assert 'attachment; filename=' in response['Content-Disposition']
    
    content = response.content.decode('utf-8')
    lines = content.strip().split('\n')
    assert len(lines) == 2  # Header + one data row
    
    header = lines[0].split(',')
    header[len(header) - 1] = header[len(header) - 1].strip()  # removes '\r' if added at the end of the line
    expected_headers = TOTAL_DETAILS_HEADERS_CSV
    assert header == expected_headers
    
    data = lines[1].split(',')
    assert data[0] == 'AAPL'
    assert data[len(expected_headers) -1] == '5000'