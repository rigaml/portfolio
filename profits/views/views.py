from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

from profits.models import Broker, Currency, Dividend, Operation, Split
from profits.serializers import BrokerSerializer, CurrencySerializer, DividendSerializer, OperationSerializer, SplitSerializer
from profits.views.base_view import BaseViewSet

class BrokerViewSet(BaseViewSet):
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer

    def destroy(self, request, pk):
        broker= get_object_or_404(Broker, pk=pk)
        if broker.account_set.exists():   # type: ignore (Pylance does not get `broker.account_set` reference)
            return Response({'error': 'Broker cannot be deleted because record is associated with another table'}, 
                status=status.HTTP_400_BAD_REQUEST)

        broker.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CurrencyViewSet(BaseViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def destroy(self, request, pk):
        currency= get_object_or_404(Currency, pk=pk)
        if (currency.origin_currencyexchange.exists() or  # type: ignore
           currency.target_currencyexchange.exists() or   # type: ignore
           currency.dividend_set.exists() or    # type: ignore
           currency.operation_set.exists()):    # type: ignore
            return Response({'error': 'Currency cannot be deleted because record is associated with another table'}, 
                status=status.HTTP_400_BAD_REQUEST)

        currency.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DividendViewSet(BaseViewSet):
    queryset = Dividend.objects.select_related('currency')
    serializer_class = DividendSerializer