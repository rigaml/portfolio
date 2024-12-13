from datetime import datetime
from decimal import Decimal
from io import StringIO
import csv

from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from profits.models import Split
from profits.serializers import SplitSerializer
from profits.views.base_view import BaseViewSet


class SplitViewSet(BaseViewSet):
    queryset = Split.objects.all()
    serializer_class = SplitSerializer

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def upload(self, request):
        """
        Uplodad splits from a file:
        ```bash
        curl -H "Authorization: Token <admin_token>"  \
             -X POST 127.0.0.1:8000/profits/split/upload/ \
             -F "file=@profits/data/splits.csv"
        ```
        """
        file = request.FILES.get("file")

        if not all([file]):
            return Response(
                {"error": "`file` is a required parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            csv_file = file.read().decode('utf-8')
            csv_data = csv.DictReader(StringIO(csv_file))

            splits = []
            for row in csv_data:
                try:
                    date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
                    ticker = row["Ticker"]
                    origin = Decimal(row["Origin"])
                    target = Decimal(row["Target"])
                except (KeyError, ValueError) as e:
                    return Response(
                        {"error": f"Invalid row format or data: {row}, error: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                splits.append((date, ticker, origin, target))

            with transaction.atomic():
                for date, ticker, origin, target in splits:
                    Split.objects.update_or_create(
                        # parameters deciding if update or create are ones in `unique_together`
                        date=date, ticker=ticker, 
                        defaults={"origin": origin, "target": target},
                    )

            return Response({
                'message': f'Successfully imported {len(splits)} splits'
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
             -X DELETE 127.0.0.1:8000/profits/split/bulk_delete/
        """
        deleted_count, _ = Split.objects.all().delete()

        return Response({
            'message': f'Successfully deleted {deleted_count} splits'
        })
