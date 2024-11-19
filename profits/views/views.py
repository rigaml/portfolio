from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from profits.models import Broker, Currency, Dividend, Operation, Split
from profits.permissions import IsAdminOrReadOnly
from profits.serializers import BrokerSerializer, CurrencySerializer, DividendSerializer, OperationSerializer, SplitSerializer

class BrokerViewSet(ModelViewSet):
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer

    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, pk):
        broker= get_object_or_404(Broker, pk=pk)
        if broker.account_set.exists():   # type: ignore
            return Response({'error': 'Broker cannot be deleted because record is associated with another table'})

        broker.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CurrencyViewSet(ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, pk):
        currency= get_object_or_404(Currency, pk=pk)
        if (currency.origin_currencyexchange.exists() or  # type: ignore
           currency.target_currencyexchange.exists() or   # type: ignore
           currency.dividend_set.exists() or    # type: ignore
           currency.operation_set.exists()):    # type: ignore
            return Response({'error': 'Currency cannot be deleted because record is associated with another table'})

        currency.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class SplitViewSet(ModelViewSet):
    queryset = Split.objects.all()
    serializer_class = SplitSerializer

    permission_classes = [IsAdminOrReadOnly]


class DividendViewSet(ModelViewSet):
    queryset = Dividend.objects.all()
    serializer_class = DividendSerializer

    permission_classes = [IsAdminOrReadOnly]

class OperationViewSet(ModelViewSet):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer

    permission_classes = [IsAdminOrReadOnly]
