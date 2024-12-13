from datetime import datetime
from decimal import Decimal
from io import StringIO
import csv

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from profits.models import Currency, CurrencyExchange
from profits.pagination import DefaultPagination
from profits.permissions import IsAdminOrReadOnly
from profits.serializers import CurrencyExchangeSerializer
from profits.views.currency_exchange_filter import CurrencyExchangeFilter


class CurrencyExchangeViewSet(ReadOnlyModelViewSet):
    queryset = CurrencyExchange.objects.select_related('origin', 'target')
    serializer_class = CurrencyExchangeSerializer

    # pagination_class = DefaultPagination

    # filter_backends = [DjangoFilterBackend]
    # filterset_class = CurrencyExchangeFilter
    # permission_classes = [IsAdminOrReadOnly] 

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def upload(self, request):
        """
        Uplodad currency exchanges from a file:
        ```bash
        curl -H "Authorization: Token <admin_token>"  \
             -X POST 127.0.0.1:8000/profits/currency-exchange/upload/ \
             -F "file=@profits/data/currency_exchanges/bankofengland-gbp-eur.csv" \
             -F "origin=GBP" \
             -F "target=EUR"
        ```
        """
        origin_code = request.data.get('origin')
        target_code = request.data.get('target')
        file = request.FILES.get("file")

        if not all([origin_code, target_code, file]):
            return Response(
                {"error": "`origin`, `target` and `file` are required parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        origin = get_object_or_404(Currency, iso_code=origin_code)
        target = get_object_or_404(Currency, iso_code=target_code)

        try:
            csv_file = file.read().decode('utf-8')
            csv_data = csv.DictReader(StringIO(csv_file))

            exchanges = []
            for row in csv_data:
                try:
                    date = datetime.strptime(row["Date"], "%d %b %y").date()
                    rate = Decimal(row["ExchangeRate"])
                except (KeyError, ValueError) as e:
                    return Response(
                        {"error": f"Invalid row format or data: {row}, error: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                exchanges.append((date, rate))

            with transaction.atomic():
                for date, rate in exchanges:
                    CurrencyExchange.objects.update_or_create(
                        # parameters deciding if update or create are ones in `unique_together`
                        date=date, origin=origin, target=target, 
                        defaults={"rate": rate},
                    )

            return Response({
                'message': f'Successfully imported {len(exchanges)} exchange rates'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"])
    def bulk_delete(self, request):
        """
        Delete all exchanges between two currencies
        curl -H "Authorization: Token <admin_token>"  \
             -X DELETE 127.0.0.1:8000/profits/currency-exchange/bulk_delete/?origin=GBP&target=EUR    
        """
        origin_code = request.query_params.get('origin')
        target_code = request.query_params.get('target')

        if not all([origin_code, target_code]):
            return Response({
                'error': '`origin` and `target` currencies are required querystrings'
            }, status=status.HTTP_400_BAD_REQUEST)

        origin = get_object_or_404(Currency, iso_code=origin_code)
        target = get_object_or_404(Currency, iso_code=target_code)

        deleted_count, _ = CurrencyExchange.objects.filter(
            origin=origin,
            target=target
        ).delete()

        return Response({
            'message': f'Successfully deleted {deleted_count} exchange rates'
        })
