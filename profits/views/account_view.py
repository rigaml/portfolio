from datetime import datetime
from typing import Optional, Tuple, Union
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from profits.models import Account
from profits.permissions import IsAdminOrReadOnly
from profits.serializers import AccountSerializer
from profits.services.currency_service import CurrencyService
from profits.repositories.currency_repository import CurrencyRepository
from profits.repositories.operation_repository import OperationRepository
from profits.services.profit_calculator import ProfitCalculator
from profits.services.profit_exchanger import ProfitExchanger
from profits.utils import datetime_utils, csv_utils
from profits.services.profit_service import ProfitService


class ProfitServiceFactory:
    def create(self, date_end):
        # Using 'None' as should take currencies before the data as posibility operation 
        # was in a bank holiday and need to take a previous conversion
        currency_service = CurrencyService(CurrencyRepository(), None, date_end)
        operation_repository= OperationRepository()
        profit_calculator= ProfitCalculator(ProfitExchanger(currency_service))
        return ProfitService(operation_repository, currency_service, profit_calculator)

class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    # permission_classes = [IsAdminOrReadOnly]

    def __init__(self, *args, **kwargs):
        """Setting dependecy factory in the init"""
        super().__init__(*args, **kwargs)
        self.profit_service_factory = ProfitServiceFactory()

    def _get_account_and_service(self, request, pk) -> Tuple[Optional[Account], Optional[datetime], Optional[datetime], Union[ProfitService, Response]]:
    
        """
        Common function to retrieve account, parse dates, and initialize profit service.
        """
        # Retrieve account object
        try:
            account = self.get_object()
        except Account.DoesNotExist:
            return None, None, None, Response({"error": "Account not found."}, status=404)

        # Parse dates
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')

        try:
            date_start = datetime_utils.parse_flexible_date(date_start)
            date_end = datetime_utils.parse_flexible_date(date_end)
        except ValueError:
            return None, None, None, Response({"error": f"Invalid date format `{date_start}` or `{date_end}`."}, status=400)

        try:
            profit_service = self.profit_service_factory.create(date_end)
        except Exception as e:
            return None, None, None, Response({"error": "Error initializing profit service."}, status=400)

        return account, date_start, date_end, profit_service

    def destroy(self, request, pk):
        account= get_object_or_404(Account, pk=pk)
        if account.operation_set.exists():   # type: ignore
            return Response(
                {'error': 'Account cannot be deleted because record is associated with another table'}, 
                status=status.HTTP_400_BAD_REQUEST)

        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path='total')
    def total(self, request, pk=None):
        """
        Get profits total number.
        http://127.0.0.1:8000/profits/account/1/total?date_start=2023-01-01&date_end=2023-12-31

        """
        account, date_start, date_end, profit_service_or_response = self._get_account_and_service(request, pk)
        if isinstance(profit_service_or_response, Response):
            return profit_service_or_response

        # Avoid Pylance complaining about account 'None'
        if account is None: 
            raise ValueError("`account` cannot be None")

        try:
            profit_total = profit_service_or_response.get_total(account, date_start, date_end)
        except Exception:
            return Response({"error": f"There was an error calculating total amount for account {account} between dates `{date_start}` or `{date_end}`."}, status=400)

        params = {
            'id': account.id,
            'date_start': date_start,
            'date_end': date_end,
            'profit_total': profit_total
        }
        return Response(params)


    @action(detail=True, methods=["get"], url_path='total-details')
    def total_details(self, request, pk=None):
        """
        Lists details of buy and sell operations used to calculate profits.
        http://127.0.0.1:8000/profits/account/1/total-details?date_start=2023-01-01&date_end=2023-12-31
        """
        account, date_start, date_end, profit_service_or_response = self._get_account_and_service(request, pk)
        if isinstance(profit_service_or_response, Response):
            return profit_service_or_response

        # Avoid Pylance complaining about account 'None'
        if account is None: 
            raise ValueError("`account` cannot be None")
                
        try:
            tickers_profit = profit_service_or_response.get_total_details(account, date_start, date_end)
        except Exception:
            return Response({"error": f"There was an error calculating total details for account {account} between dates `{date_start}` or `{date_end}`."}, status=400)

        return csv_utils.generate_total_details_csv(tickers_profit, account.id, date_start, date_end)