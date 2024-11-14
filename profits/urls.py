from django.urls import path
from . import views

urlpatterns = [
    path('brokers/', views.BrokerList.as_view(), name='broker_list'),
    path('brokers/<str:broker_name>/totals', views.get_totals, name='get_totals'),
    path('brokers/<str:broker_name>/details', views.get_details, name='get_details'),
    path('currencies/', views.CurrencyView.as_view(), name='currency_list'),
    path('currency-exchanges/', views.CurrencyExchangeView.as_view(), name='currency-exchanges'),    
    path('operations/<str:broker_name>/', views.OperationList.as_view(), name='operation_list'),
    path('currency-exchanges/<str:origin>/<str:target>/', views.CurrencyExchangeList.as_view(), name='currency_exchange_list'),
    path('splits/', views.SplitList.as_view(), name='split_list'),
    path('dividends/', views.DividendList.as_view(), name='dividend_list'),
]
