import csv

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from profits.models import Account, Operation
from profits.permissions import IsAdminOrReadOnly
from profits.serializers import AccountSerializer


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    # permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, pk):
        account= get_object_or_404(Account, pk=pk)
        if broker.account_set.exists():   # type: ignore
            return Response({'error': 'Account cannot be deleted because record is associated with another table'})

        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path='total')
    def total(self, request, pk=None):
        """
        http://127.0.0.1:8000/profits/accounts/1/total?date_start=2023-01-01&date_end=2023-12-31

        """
        try:
            account = self.get_object()
        except Account.DoesNotExist:
            return Response({"detail": "Account not found."}, status=404)
        
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')

        try:
            date_start = parse_datetime(date_start) if date_start else None
            date_end = parse_datetime(date_end) if date_end else None
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SS')."},
                status=400
            )

        operations = Operation.objects.filter(account=account)
        if date_start:
            operations = operations.filter(date__gte=date_start)
        if date_end:
            operations = operations.filter(date__lte=date_end)

        data = {
            'id': account.id,
            'date_start': date_start,
            'date_end': date_end,
            'amount_total': 10000
        }
        return Response(data)

    @action(detail=True, methods=["get"], url_path='operations-csv')
    def operations_csv(self, request, pk=None):
        """
        http://127.0.0.1:8000/profits/accounts/1/operations-csv/?date_start=2022-01-01&date_end=2024-12-31
        """
        try:
            account = self.get_object()
        except Account.DoesNotExist:
            return Response({"detail": "Account not found."}, status=404)

        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')

        try:
            date_start = parse_datetime(date_start) if date_start else None
            date_end = parse_datetime(date_end) if date_end else None
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SS')."},
                status=400
            )

        operations = Operation.objects.filter(account=account)
        if date_start:
            operations = operations.filter(date__gte=date_start)
        if date_end:
            operations = operations.filter(date__lte=date_end)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="operations_account_{pk}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Date', 'Type', 'Ticker', 'Quantity',
            'Currency', 'Amount Total', 'Exchange'
        ])
        for operation in operations:
            writer.writerow([
                operation.date, operation.type, operation.ticker,
                operation.quantity, operation.currency.name,
                operation.amount_total, operation.exchange
            ])

        return response