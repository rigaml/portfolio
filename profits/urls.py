from django.urls import path
from . import views

urlpatterns = [
    path('brokers/', views.broker_list, name='broker_list'),
    path('brokers/<str:broker_short_name>/totals', views.get_totals, name='get_totals'),
    path('brokers/<str:broker_short_name>/details', views.get_details, name='get_details'),
    path('currencies/', views.currency_list, name='currency_list'),
    path('operations/<str:broker_short_name>/', views.operation_list, name='operation_list'),
    path('currency-exchanges/<str:origin>/<str:target>/', views.currency_exchange_list, name='currency_exchange_list'),
    path('splits/', views.split_list, name='split_list'),
    path('dividends/', views.dividend_list, name='dividend_list'),
]
