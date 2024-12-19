from datetime import datetime, timezone
from profits.utils.csv_utils import generate_total_details_csv


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
    expected_headers = [
        'Ticker', 'Sell Date', 'Sell Quantity', 'Sell Amount Total',
        'Sell Currency', 'Buy Date', 'Buy Quantity', 'Buy Amount Total', 'Profit'
    ]
    assert header == expected_headers


def test_generate_total_details_csv_when_one_detail_returns_correct_csv():
    total_details = [{
            'ticker': 'AAPL',
            'profit_detail': [{
                'date': '2023-06-01',
                'quantity': 100,
                'amount_total': 15000,
                'currency': 'USD',
                'buy_date': '2023-01-15',
                'buy_quantity': 100,
                'buy_amount_total': 10000,
                'profit': 5000
            }]
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
    expected_headers = [
        'Ticker', 'Sell Date', 'Sell Quantity', 'Sell Amount Total',
        'Sell Currency', 'Buy Date', 'Buy Quantity', 'Buy Amount Total', 'Profit'
    ]
    assert header == expected_headers
    
    data = lines[1].split(',')
    assert data[0] == 'AAPL'
    assert data[len(expected_headers) -1] == '5000'