from rest_framework import serializers

from profits.models import Account, Broker, Currency, CurrencyExchange, Dividend, Operation, Split


class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broker
        fields = ['id', 'name', 'full_name', 'created_at']
        read_only_fields = ['id', 'created_at']

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'iso_code', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class CurrencyExchangeSerializer(serializers.ModelSerializer):
    origin = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()

    def get_origin(self, obj):
        return obj.origin.iso_code

    def get_target(self, obj):
        return obj.target.iso_code
    
    class Meta:
        model = CurrencyExchange
        fields = ['id', 'date', 'origin', 'target', 'rate', 'created_at']
        read_only_fields = ['id', 'created_at']

class SplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Split
        fields = ['id', 'date', 'ticker', 'origin', 'target', 'created_at']
        read_only_fields = ['id', 'created_at']

class DividendSerializer(serializers.ModelSerializer):
    currency = serializers.SlugRelatedField(
        queryset=Currency.objects.all(), slug_field='iso_code'
    )

    class Meta:
        model = Dividend
        fields = ['id', 'date', 'ticker', 'currency', 'amount_total', 'created_at']
        read_only_fields = ['id', 'created_at']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'user', 'broker', 'user_broker_ref', 'user_own_ref', 'created_at']
        read_only_fields = ['id', 'created_at']


class OperationSerializer(serializers.ModelSerializer):
    currency = serializers.SlugRelatedField(
        queryset=Currency.objects.all(), slug_field='iso_code'
    )
    
    class Meta:
        model = Operation
        fields = ['id', 'account', 'date', 'type', 'ticker', 'quantity', 'currency', 'amount_total', 'exchange', 'created_at']
        read_only_fields = ['id', 'created_at']

