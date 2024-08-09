from django.shortcuts import render
from django.http import HttpResponse

def get_total(request, broker: str):
    """    
    http://127.0.0.1:8000/profits/total/ING?date_start=2023-01-01&date_end=2023-12-31
    """
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    return render(request, 'profit_total.html', {'broker': broker, 'date_start': date_start, 'date_end': date_end})

def get_details(request, broker: str):
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    return render(request, 'profit_details.html', {'broker': broker, 'date_start': date_start, 'date_end': date_end})