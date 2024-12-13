from io import StringIO
from decimal import Decimal
import csv

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from profits.models import Account, Currency, Operation
from profits.pagination import DefaultPagination
from profits.permissions import IsAdminOrReadOnly
from profits.serializers import OperationSerializer
from profits.utils import datetime_utils
from profits.views.base_view import BaseViewSet


class OperationViewSet(BaseViewSet):
    queryset = Operation.objects.select_related('currency')
    serializer_class = OperationSerializer

    # pagination_class = DefaultPagination

    # filter_backends = [DjangoFilterBackend]
    # filterset_class = CurrencyExchangeFilter
    # permission_classes = [IsAdminOrReadOnly] 

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def upload(self, request):
        """
        Uplodad a Csv file with operations for an account:
        ```bash
        curl -H "Authorization: Token <admin_token>"  \
            -X POST 127.0.0.1:8000/profits/operation/upload/ \
            -F "account_id=<account_id>" \
            -F "file=@profits/data/upload/stock-operations-II.csv"
        ```
        """
        account_id = request.data.get('account_id')
        file = request.FILES.get("file")

        if not all([account_id, file]):
            return Response(
                {"error": "`account_id` and `file` are required parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        account = get_object_or_404(Account, id=account_id)
        
        try:
            csv_file = file.read().decode('utf-8')
            csv_data = csv.DictReader(StringIO(csv_file))

            operations = []
            for row in csv_data:
                try:
                    type_op = row["Type"].upper()
                    date = datetime_utils.to_datetime_tz_aware(row["Date"])
                    quantity = Decimal(row["Quantity"])
                    ticker = row["Ticker"].upper()
                    price = Decimal(row.get("Price", 0))
                    amount_total = Decimal(row["Amount Total"])
                    currency_code= row.get("Currency", "USD")
                    currency = Currency.objects.filter(iso_code=currency_code).first()
                    exchange = Decimal(row.get("Exchange", 1))
                except (KeyError, ValueError) as e:
                    return Response(
                        {"error": f"Invalid row format or data: {row}, error: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                operations.append((type_op, date, quantity, ticker, price, amount_total, currency, exchange))

            with transaction.atomic():
                for type_op, date, quantity, ticker, price, amount_total, currency, exchange in operations:
                    Operation.objects.update_or_create(
                        # parameters deciding if update or create are ones in `unique_together`
                        account=account, date=date, ticker=ticker, 
                        defaults={"type": type_op, "quantity": quantity, "currency": currency, "amount_total": amount_total, "exchange": exchange},
                    )

            return Response({
                'message': f'Successfully imported {len(operations)} operations'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(str(e))
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)        

    @action(detail=False, methods=["delete"])
    def bulk_delete(self, request):
        """
        Delete all operations for a specified account.
        curl -H "Authorization: Token <admin_token>"  \
             -X DELETE 127.0.0.1:8000/profits/operation/bulk_delete/?account_id=<account_id>
        """
        account_id = request.query_params.get('account_id')

        if not all([account_id]):
            return Response({
                'error': '`account_id` is a required querystring'
            }, status=status.HTTP_400_BAD_REQUEST)

        account = get_object_or_404(Account, id=account_id)

        deleted_count, _ = Operation.objects.filter(
            account= account
        ).delete()

        return Response({
            'message': f'Successfully deleted {deleted_count} operations'
        })
