from django.db import models

class Broker(models.Model):
    name = models.CharField(max_length=10, unique=True)
    full_name= models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

class Currency(models.Model):
    iso_code = models.CharField(max_length=3, unique=True)
    description = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
class Operation(models.Model):
    TYPE_CHOICES = [
        # Merge between 2 companies can be SELL from one at for the original BUY value and BUY from new with the original BUY from first?? 
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    date = models.DateTimeField()
    broker = models.ForeignKey(Broker, on_delete=models.PROTECT)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    ticker = models.CharField(max_length=10)
    exchange = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=15, decimal_places=7) #Fractional shares require decimal_places
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount_total = models.DecimalField(max_digits=17, decimal_places=7)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'broker', 'ticker', 'exchange')


class CurrencyExchange(models.Model):
    date = models.DateTimeField()
    origin = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='origin_currencyexchange')
    target = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='target_currencyexchange')
    rate = models.DecimalField(max_digits=10, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'origin', 'target')

class Split(models.Model):
    date = models.DateTimeField()
    ticker = models.CharField(max_length=5)
    origin = models.DecimalField(max_digits=5, decimal_places=2)
    target = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'ticker')

class Dividend(models.Model):
    date = models.DateTimeField()
    ticker = models.CharField(max_length=5)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount_total = models.DecimalField(max_digits=17, decimal_places=7)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'ticker')