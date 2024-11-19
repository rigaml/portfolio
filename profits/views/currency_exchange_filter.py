from django_filters import rest_framework as filters
from profits.models import CurrencyExchange

class CurrencyExchangeFilter(filters.FilterSet):
    origin = filters.CharFilter(field_name="origin__name", lookup_expr='exact')  # Filter by origin currency name
    target = filters.CharFilter(field_name="target__name", lookup_expr='exact')  # Filter by target currency name
    date_from = filters.DateFilter(field_name="date", lookup_expr='gte')  # Greater than or equal
    date_to = filters.DateFilter(field_name="date", lookup_expr='lte')    # Less than or equal

    class Meta:
        model = CurrencyExchange
        fields = ['origin', 'target', 'date_from', 'date_to']
