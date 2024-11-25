import pytest
from typing import Any, Callable, Optional, Type
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import make_aware

from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client() -> APIClient:
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(
        username: str = 'testuser',
        email: str = 'test@example.com',
        password: str = 'testpass123',
        is_staff: bool = False,
        is_superuser: bool = False,
        **extra_fields: Any
    ) -> AbstractUser:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        return user
    return _create_user

@pytest.fixture
def user(create_user: Callable[..., AbstractUser]) -> AbstractUser:
    return create_user()

@pytest.fixture
def authenticated_client(api_client: APIClient):
    def _get_authenticated_client(user: Optional[AbstractUser] = None) -> APIClient:
        if user is None:
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
        api_client.force_authenticate(user=user)
        return api_client
    return _get_authenticated_client

@pytest.fixture
def date_factory():
    def _create_date(date_str: str) -> datetime:
        return make_aware(datetime.fromisoformat(date_str))
    return _create_date

@pytest.fixture
def model_factory():
    """
    Model factory fixture for creating generic model instances.
    """
    def _create_model(model_class: Type, **kwargs: Any) -> Any:
        return model_class.objects.create(**kwargs)
    return _create_model

@pytest.fixture
def create_currency(model_factory: Callable[..., Any]):
    def _create_currency(**kwargs: Any) -> Any:
        from profits.models import Currency  # Import here to avoid circular imports
        return model_factory(Currency, **kwargs)
    return _create_currency

@pytest.fixture
def create_exchange(model_factory: Callable[..., Any]):
    def _create_exchange(**kwargs: Any) -> Any:
        from profits.models import CurrencyExchange  # Import here to avoid circular imports
        return model_factory(CurrencyExchange, **kwargs)
    return _create_exchange