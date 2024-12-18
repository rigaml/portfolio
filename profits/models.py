from uuid import uuid4
from django.db import models

from portfolio import settings

class Broker(models.Model):
    name = models.CharField(max_length=10, unique=True)
    full_name= models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

class Currency(models.Model):
    iso_code = models.CharField(max_length=3, unique=True)
    description = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
class CurrencyExchange(models.Model):
    date = models.DateField()
    origin = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='origin_currencyexchange')
    target = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='target_currencyexchange')
    rate = models.DecimalField(max_digits=10, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'origin', 'target')

class Split(models.Model):
    date = models.DateField()
    ticker = models.CharField(max_length=5)
    origin = models.DecimalField(max_digits=5, decimal_places=2)
    target = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'ticker')

class Dividend(models.Model):
    date = models.DateField()
    ticker = models.CharField(max_length=5)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount_total = models.DecimalField(max_digits=17, decimal_places=7)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'ticker')

class Account(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    broker = models.ForeignKey(Broker, on_delete=models.PROTECT)
    # reference provided by the broker to identify the account
    user_broker_ref = models.CharField(max_length=255)
    # reference set by the user to identify his accounts
    user_own_ref = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('broker', 'user_broker_ref')    

class Operation(models.Model):
    TYPE_CHOICES = [
        # Merge between 2 companies can be SELL from one at for the original BUY value and BUY from new with the original BUY from first?? 
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    date = models.DateTimeField()
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    ticker = models.CharField(max_length=10)
    # Fractional shares require decimal_places
    quantity = models.DecimalField(max_digits=15, decimal_places=7) 
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount_total = models.DecimalField(max_digits=17, decimal_places=7)
    # Currency exchange as provided by the broker at the time of the operation
    exchange = models.DecimalField(max_digits=10, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('account', 'date', 'ticker')


