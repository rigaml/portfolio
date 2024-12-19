from django.contrib import admin

from profits import models

class CustomModelAdmin(admin.ModelAdmin):
    # Base class to format the dates as yyyy-mm-dd
    def format_date(self, obj, field_name):
        date_value = getattr(obj, field_name, None)
        if date_value:
            return date_value.strftime('%Y-%m-%d')
        return "-"
    format_date.short_description = 'Date'

    def format_datetime(self, obj, field_name):
        datetime_value = getattr(obj, field_name, None)
        if datetime_value:
            return datetime_value.strftime('%Y-%m-%d %H:%M:%S')
        return "-"
    format_datetime.short_description = 'DateTime'

@admin.register(models.Broker)
class BrokerAdmin(CustomModelAdmin):
    list_display = ['name', 'full_name']

    ordering = ['name']

    list_per_page = 10

@admin.register(models.Currency)
class CurrencyAdmin(CustomModelAdmin):
    list_display = ['iso_code', 'description']

    ordering = ['iso_code']

    list_per_page = 10    


@admin.register(models.CurrencyExchange)
class CurrencyExchangeAdmin(CustomModelAdmin):
    list_display = ['formatted_date', 'origin', 'target', 'rate']

    ordering = ['date', 'origin', 'target']
    
    list_per_page = 30

    def formatted_date(self, obj):
        return self.format_date(obj, 'date')

@admin.register(models.Split)
class SplitAdmin(CustomModelAdmin):
    list_display = ['formatted_date', 'ticker', 'origin', 'target']

    ordering = ['date', 'ticker']
    
    list_per_page = 30

    def formatted_date(self, obj):
        return self.format_date(obj, 'date')    

@admin.register(models.Dividend)
class DividendAdmin(CustomModelAdmin):
    list_display = ['formatted_date', 'ticker', 'amount_total', 'currency']

    ordering = ['date', 'ticker']
    
    list_per_page = 30

    def formatted_date(self, obj):
        return self.format_date(obj, 'date')    

@admin.register(models.Account)
class AccountAdmin(CustomModelAdmin):
    list_display = ['user', 'user_broker_ref', 'user_own_ref']

    ordering = ['user']
    
    list_per_page = 30

@admin.register(models.Operation)
class OperationAdmin(CustomModelAdmin):
    list_display = ['account', 'formatted_datetime', 'type', 'ticker', 'quantity', 'amount_total', 'currency', 'exchange']

    ordering = ['account', 'date']
    
    list_per_page = 30

    def formatted_datetime(self, obj):
        return self.format_datetime(obj, 'date')    
