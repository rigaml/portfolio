from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock
import pytest

from profits.repositories.currency_repository import CurrencyRepository
from profits.services.currency_service import CurrencyService
from profits.services.exceptions import CurrencyConversionException, CurrencyExchangeNotFoundException


class TestCurrencyService:
    @pytest.fixture
    def currency_repository_mock(self):
        return Mock(spec=CurrencyRepository)

    @pytest.fixture
    def currency_service_mock(self, currency_repository_mock):
        date_start = datetime(2024, 1, 1)
        date_end = datetime(2024, 12, 31)
        return CurrencyService(
            currency_repository=currency_repository_mock,
            date_start=date_start,
            date_end=date_end,
        )

    @pytest.mark.parametrize(
        "currency_pair, expected_result",
        [
            ("USDGBP", True),
            ("USDEUR", True),
            ("GBPUSD", True),
            ("GBPEUR", True),
            ("EURUSD", True),
            ("EURGBP", True),
            ("AAPL", False),
            ("TSLA", False),
        ]
    )

    def test_is_currency_conversion(self, currency_service_mock, currency_pair, expected_result):
        assert currency_service_mock.is_currency_conversion(currency_pair) == expected_result

    def test_get_currency_exchange_when_same_currency_returns_1(self, currency_service_mock, currency_repository_mock):
        result = currency_service_mock.get_currency_exchange(
            "USD", "USD", datetime(2024, 1, 1)
        )
        assert result == Decimal("1")
        currency_repository_mock.get_currency_exchanges.assert_not_called()

    def test_get_currency_exchange_when_no_rates_found_raises_exception(self, currency_service_mock, currency_repository_mock):

        currency_repository_mock.get_currency_exchanges.return_value = {}
        
        with pytest.raises(CurrencyExchangeNotFoundException) as exc_info:
            currency_service_mock.get_currency_exchange(
                "USD", "GBP", datetime(2024, 1, 3)
            )

        assert "No exchange rates found for USD-GBP" in str(exc_info.value)


    def test_get_currency_exchange_when_no_rate_for_date_found_raises_exception(self, currency_service_mock, currency_repository_mock):

        mock_exchange_data = {
            datetime(2024, 2, 1).date(): Decimal("1.25"),
        }
        currency_repository_mock.get_currency_exchanges.return_value = mock_exchange_data
        
        with pytest.raises(CurrencyConversionException) as exc_info:
            currency_service_mock.get_currency_exchange(
                "USD", "GBP", datetime(2024, 1, 3)
            )

        assert "Exchange for USD-GBP could not be found" in str(exc_info.value)
    def test_get_currency_exchange_when_exchange_exist_on_the_date_then_returns_rate(self, currency_service_mock, currency_repository_mock):

        mock_exchange_data = {
            datetime(2024, 1, 1).date(): Decimal("1.25"),
            datetime(2024, 1, 2).date(): Decimal("1.33"),
        }
        currency_repository_mock.get_currency_exchanges.return_value = mock_exchange_data

        result = currency_service_mock.get_currency_exchange(
            "USD", "GBP", datetime(2024, 1, 2)
        )

        assert result == Decimal("1.33")
        currency_repository_mock.get_currency_exchanges.assert_called_once_with(
            "USD", "GBP", currency_service_mock.date_start, currency_service_mock.date_end
        )

    def test_get_currency_exchange_when_exact_date_doesnt_exist_returns_previous_date(self, currency_service_mock, currency_repository_mock):

        mock_exchange_data = {
            datetime(2024, 1, 1).date(): Decimal("1.25"),
        }
        currency_repository_mock.get_currency_exchanges.return_value = mock_exchange_data

        result = currency_service_mock.get_currency_exchange(
            "USD", "GBP", datetime(2024, 1, 3)
        )

        assert result == Decimal("1.25")
