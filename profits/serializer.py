from rest_framework import serializers

from profits.models import Broker, Currency, CurrencyExchange, Operation


class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broker
        fields = ['short_name', 'name', 'created']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['iso_code', 'description', 'created']

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ['date', 'broker', 'currency', 'type', 'quantity', 'ticker', 'amount_total', 'created']

class CurrencyExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = ['date', 'origin', 'target', 'rate', 'created']

class SplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = ['date', 'origin', 'target', 'rate', 'created']

class DividendSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = ['date', 'origin', 'target', 'rate', 'created']