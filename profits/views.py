from django.http import HttpResponse, JsonResponse
import csv

def get_total(request, broker: str):
    """    
    http://127.0.0.1:8000/profits/total/ING?date_start=2023-01-01&date_end=2023-12-31
    """
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    data = {
        'date_start': date_start,
        'date_end': date_end,
        'broker': broker,
        'total': 10000
    }
    return JsonResponse(data)

def get_details(request, broker: str):
    """
    http://127.0.0.1:8000/profits/details/ING?date_start=2022-01-01&date_end=2024-12-31
    """
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{date_start}-{date_end}-{broker}-profits-details.csv"'

    # Create a CSV writer using the response as the "file"
    writer = csv.writer(response)
    
    # Write the header (optional)
    writer.writerow(['Ticker', 'Quantity', 'Currency', 'Buy Date', 'Buy Amount', 'Sell Date', 'SellAmount', 'Profit'])

    # Write data rows
    data = [
        ['RXRX', '10', 'USD', '2023-01-01', '100', '2024-02-01', '200', '100'],
        ['TSLA', '100', 'USD', '2023-02-01', '100', '2024-02-02', '2000', '1900'],
        ['NVDA', '1000', 'USD', '2022-03-01', '100', '2024-02-03', '20000', '19900'],
    ]
    
    for row in data:
        writer.writerow(row)

    return response