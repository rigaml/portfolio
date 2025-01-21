from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock
import pytest
from profits.interfaces.dtos.profit_dto import ProfitDTO, ProfitExchangeDTO
from profits.services.currency_service import CurrencyService
from profits.services.profit_exchanger import ProfitExchanger


class TestExchangeCurrencies:
    @pytest.fixture
    def currency_service_mock(self):
        return Mock(spec=CurrencyService)
    
    @pytest.fixture
    def profit_exchanger(self, currency_service_mock):
        return ProfitExchanger(currency_service=currency_service_mock)
    
    @pytest.fixture
    def sample_profit_dto(self):
        return ProfitDTO(
            buy_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            buy_amount_total=Decimal(1000),
            buy_currency='GBP',
            sell_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
            sell_quantity=Decimal(10),
            sell_amount_total=Decimal(1200),
            sell_currency='GBP',
            profit=Decimal(200)
        )
    
    def test_exchange_currencies_when_exchange_returns_correct_values(
            self, 
            profit_exchanger, 
            currency_service_mock, 
            sample_profit_dto
    ):
        target_currency = 'GBP'
        currency_service_mock.get_currency_exchange.side_effect = [
            Decimal(1), 
            Decimal(2)
        ]

        result = profit_exchanger.exchange_currencies(sample_profit_dto, target_currency)

        assert isinstance(result, ProfitExchangeDTO)
        assert result.buy_exchange == Decimal(1)
        assert result.sell_exchange == Decimal(2)
        assert result.buy_amount_total_exchange == Decimal(1000)
        assert result.sell_amount_total_exchange == Decimal(2400)
        assert result.profit_exchange == Decimal(1400)
        assert currency_service_mock.get_currency_exchange.call_count == 2