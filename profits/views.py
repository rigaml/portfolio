import re
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import csv

from profits.models import Broker, Currency, CurrencyExchange, Dividend, Operation, Split
from profits.serializer import BrokerSerializer, CurrencyExchangeSerializer, CurrencySerializer, DividendSerializer, OperationSerializer, SplitSerializer

from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet


class BrokerList(APIView):
    def get(self, request):
        brokers = Broker.objects.all()
        serializer = BrokerSerializer(brokers, many=True)
        return Response(serializer.data)

@api_view()
def get_totals(request, broker_name: str):
    """
    http://127.0.0.1:8000/profits/brokers/ING/totals?date_start=2023-01-01&date_end=2023-12-31
 
    """
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    data = {
        'date_start': date_start,
        'date_end': date_end,
        'broker': broker_name,
        'amount_total': 10000
    }
    return Response(data)

@api_view()
def get_details(request, broker_name: str):
    """
    http://127.0.0.1:8000/profits/brokers/ING/details?date_start=2022-01-01&date_end=2024-12-31
    """
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{date_start}-{date_end}-{broker_name}-profits-details.csv"'

    # Create a CSV writer using the response as the "file"
    writer = csv.writer(response)

    # Write the header (optional)
    writer.writerow(['Ticker', 'Quantity', 'Currency', 'Buy Date', 'Buy Amount', 'Sell Date', 'Sell Amount', 'Profit'])

    # Write data rows
    data = [
        ['RXRX', '10', 'USD', '2023-01-01', '100', '2024-02-01', '200', '100'],
        ['TSLA', '100', 'USD', '2023-02-01', '100', '2024-02-02', '2000', '1900'],
        ['NVDA', '1000', 'USD', '2022-03-01', '100', '2024-02-03', '20000', '19900'],
    ]

    for row in data:
        writer.writerow(row)

    return response

class CurrencyList(APIView):
    def get(self, request):
        currencies = Currency.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        return Response(serializer.data)


class OperationList(APIView):
    def get(self, request, broker_name: str):
        """
        http://127.0.0.1:8000/profits/operations/ING

        """
        broker = get_object_or_404(Broker, name=broker_name)
        operations = Operation.objects.filter(pk=broker.id)

        serializer = OperationSerializer(operations.all(), many=True)
        return Response(serializer.data)
    
    def post(self, request, broker_name: str):
        broker = get_object_or_404(Broker, name=broker_name)
        ## TODO: Should use the brokerId retrieved???
        serializer = OperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response('ok')

class CurrencyExchangeList(APIView):
    def get(self, request, origin: str, target: str):
        currency_exchange = CurrencyExchange.objects.all()
        serializer = CurrencyExchangeSerializer(currency_exchange, many=True)
        return Response(serializer.data)
   
    def post(self, request, origin: str, target: str):
        serializer = CurrencyExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response('ok')


class SplitList(APIView):
    def get(self, request):
        split = Split.objects.all()
        serializer = SplitSerializer(split, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SplitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response('ok')


class DividendList(APIView):
    def get(self, request):
        dividend = Dividend.objects.all()
        serializer = DividendSerializer(dividend, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = DividendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response('ok')
