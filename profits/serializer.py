from rest_framework import serializers

from profits.models import Broker, Currency, CurrencyExchange, Dividend, Operation, Split


class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broker
        fields = ['name', 'full_name', 'created_at']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['iso_code', 'description', 'created_at']

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ['date', 'broker', 'type', 'ticker', 'quantity', 'currency', 'amount_total', 'created_at']

class CurrencyExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = ['date', 'origin', 'target', 'rate', 'created_at']

class SplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Split
        fields = ['date', 'ticker', 'origin', 'target', 'created_at']

class DividendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dividend
        fields = ['date', 'ticker', 'currency', 'amount_total', 'created_at']