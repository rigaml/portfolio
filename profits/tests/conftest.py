import pytest

from typing import Any, Callable, Type
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import make_aware

from rest_framework.test import APIClient

from profits.models import Account, Broker, Currency, CurrencyExchange, Dividend, Operation, Split

@pytest.fixture
def create_date():
    def _create_date(date_str: str) -> datetime:
        return make_aware(datetime.fromisoformat(date_str))
    return _create_date

@pytest.fixture
def date_default(create_date) -> datetime:
    return create_date('2024-01-01T00:00:00')

@pytest.fixture
def create_model():
    """
    Model factory fixture for creating generic model instances.
    """
    def _create_model(model_class: Type, **kwargs: Any) -> Any:
        return model_class.objects.create(**kwargs)
    return _create_model

@pytest.fixture
def api_client() -> APIClient:
    return APIClient()

@pytest.fixture
def create_user(create_model) -> Callable:
    def _create_user(**kwargs) -> AbstractUser:
        defaults = {
            'username': f'user_{datetime.now().timestamp()}',
            'email': f'user_{datetime.now().timestamp()}@example.com',
            'password': 'testpass123',
            'is_staff': False,
            'is_superuser': False
        }
        defaults.update(kwargs)
        return create_model(get_user_model(), **defaults)
    return _create_user

@pytest.fixture
def user_default(create_user) -> AbstractUser:
    return create_user()

@pytest.fixture
def create_authenticated_client(api_client, user_default):
    def _get_authenticated_client(**kwargs) -> APIClient:
        user = kwargs.get('user', user_default)
        api_client.force_authenticate(user=user)
        return api_client
    return _get_authenticated_client

@pytest.fixture
def authenticated_client(create_authenticated_client) -> AbstractUser:
    return create_authenticated_client()

@pytest.fixture
def create_broker(create_model) -> Callable:
    def _create_broker(**kwargs) -> Broker:
        defaults = {
            'name': f'BRO{datetime.now().timestamp()}'[:10],
            'full_name': f'Broker {datetime.now().timestamp()}'
        }
        defaults.update(kwargs)
        return create_model(Broker, **defaults)
    return _create_broker

@pytest.fixture
def broker_default(create_broker: Callable[..., Any]) -> Broker:
    return create_broker()

@pytest.fixture
def create_currency(create_model) -> Callable:
    def _create_currency(**kwargs: Any) -> Currency:
        defaults = {
            'iso_code': 'GBP',
            'description': 'British Pound'
        }
        defaults.update(kwargs)        
        return create_model(Currency, **defaults)
    return _create_currency

@pytest.fixture
def currency_gbp(create_currency) -> Currency:
    return create_currency()

@pytest.fixture
def currency_usd(create_currency) -> Currency:
    return create_currency(iso_code='USD', description='US Dollar')

@pytest.fixture
def currency_eur(create_currency) -> Currency:
    return create_currency(iso_code='EUR', description='Euro')

@pytest.fixture
def create_currency_exchange(create_model, currency_gbp, currency_usd) -> Callable:
    def _create_exchange(**kwargs) -> CurrencyExchange:
        defaults = {
            'date': datetime.now(),
            'origin': currency_gbp,
            'target': currency_usd,
            'rate': Decimal(1.11)
        }
        defaults.update(kwargs)
        return create_model(CurrencyExchange, **defaults)
    return _create_exchange

@pytest.fixture
def currency_exchange_default(create_currency_exchange) -> CurrencyExchange:
    return create_currency_exchange()

@pytest.fixture
def create_split(create_model) -> Callable:
    def _create_split(**kwargs) -> Split:
        defaults = {
            'date': datetime.now(),
            'ticker': 'AAPL',
            'origin': Decimal(1),
            'target': Decimal(20)
        }
        defaults.update(kwargs)
        return create_model(Split, **defaults)
    return _create_split


@pytest.fixture
def split_default(create_split) -> Split:
    return create_split()

@pytest.fixture
def create_dividend(create_model, currency_gbp) -> Callable:
    def _create_dividend(**kwargs) -> Dividend:
        defaults = {
            'date': datetime.now(),
            'ticker': 'AAPL',
            'currency': currency_gbp,
            'amount_total': Decimal(108)
        }
        defaults.update(kwargs)
        return create_model(Dividend, **defaults)
    return _create_dividend


@pytest.fixture
def dividend_default(create_dividend) -> Dividend:
    return create_dividend()


@pytest.fixture
def create_account(create_model, user_default, broker_default) -> Callable:
    def _create_account(**kwargs) -> Account:
        defaults = {
            'user': user_default,
            'broker': broker_default,
            'user_broker_ref': f'REF{datetime.now().timestamp()}',
            'user_own_ref': 'UserOwnRef'
        }
        defaults.update(kwargs)
        return create_model(Account, **defaults)
    return _create_account


@pytest.fixture
def account_default(create_account) -> Account:
    return create_account()

@pytest.fixture
def create_operation(
    create_model,
    date_default, 
    account_default, 
    currency_gbp,
    type= 'BUY',
    ticker= 'AAPL',
    quantity= Decimal(10), 
    amount_total= Decimal(10000),
    exchange= Decimal(1)) -> Callable:
    def _create_operation(**kwargs) -> Operation:
        defaults = {
            'account': account_default,
            'date': date_default,
            'type':  type,
            'ticker': ticker,
            'quantity': quantity,
            'currency': currency_gbp,
            'amount_total': amount_total,
            'exchange': exchange,
        }
        defaults.update(kwargs)
        return create_model(Operation, **defaults)
    return _create_operation

@pytest.fixture
def operation_default(create_operation) -> Operation:
    return create_operation()
