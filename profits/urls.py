from django.urls import path
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from .views import views, currency_exchange_view, account_view, operation_view, split_view, health_check

router = DefaultRouter()
router.register('broker', views.BrokerViewSet)
router.register('currency', views.CurrencyViewSet)
router.register('currency-exchange', currency_exchange_view.CurrencyExchangeViewSet)
router.register('split', split_view.SplitViewSet)
router.register('dividend', views.DividendViewSet)
router.register('account', account_view.AccountViewSet)
router.register('operation', operation_view.OperationViewSet)

urlpatterns = router.urls + [
    path('health/', health_check.health_check, name='health-check'),
]