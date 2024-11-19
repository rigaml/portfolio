from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from .views import views, currency_exchange_view, account_view


router = DefaultRouter()
router.register('brokers', views.BrokerViewSet)
router.register('currencies', views.CurrencyViewSet)
router.register('currency-exchanges', currency_exchange_view.CurrencyExchangeViewSet)
router.register('splits', views.SplitViewSet)
router.register('dividends', views.DividendViewSet)
router.register('accounts', account_view.AccountViewSet)
router.register('operations', views.OperationViewSet)

urlpatterns = router.urls