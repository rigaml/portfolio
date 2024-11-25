from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from .views import views, currency_exchange_view, account_view


router = DefaultRouter()
router.register('broker', views.BrokerViewSet)
router.register('currency', views.CurrencyViewSet)
router.register('currency-exchange', currency_exchange_view.CurrencyExchangeViewSet)
router.register('split', views.SplitViewSet)
router.register('dividend', views.DividendViewSet)
router.register('account', account_view.AccountViewSet)
router.register('operation', views.OperationViewSet)

urlpatterns = router.urls