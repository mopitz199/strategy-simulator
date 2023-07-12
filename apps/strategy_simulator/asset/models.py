from django.db import models

from asset import constants as asset_constants

class Asset(models.Model):

    ASSET_TYPE_CHOICES = [
        (asset_constants.ETF_TYPE, "ETF"),
        (asset_constants.CRYPTOCURRENCY_TYPE, "Cryptocurrency"),
        (asset_constants.STOCK_TYPE, "Stock"),
        (asset_constants.COMMODITY_TYPE, "Commodity"),
        (asset_constants.FUTURE_TYPE, "Future"),
    ]

    name = models.CharField(max_length=128)
    name_slug = models.CharField(max_length=128)
    ticker = models.CharField(max_length=15)

    asset_type = models.CharField(
        max_length=30,
        choices=ASSET_TYPE_CHOICES,
        default=asset_constants.STOCK_TYPE
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Candle(models.Model):

    
    PERIODICITY_CHOICES = [
        (asset_constants.DAILY_CANDLE, "Daily Candle"),
        (asset_constants.WEEKLY_CANDLE, "Weekly Candle"),
        (asset_constants.MONTHLY_CANDLE, "Monthly Candle"),
    ]

    CURRENCY_CHOICES = [
        (asset_constants.CURRENCY_USD, "USD"),
        (asset_constants.CURRENCY_EUR, "EUR"),
    ]

    periodicity = models.CharField(
        max_length=30,
        choices=PERIODICITY_CHOICES,
        default=asset_constants.DAILY_CANDLE
    )
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default=asset_constants.CURRENCY_USD
    )

    asset = models.ForeignKey("Asset", on_delete=models.CASCADE)
    
    open_price = models.DecimalField(max_digits=15, decimal_places=4)
    close_price = models.DecimalField(max_digits=15, decimal_places=4)
    low_price = models.DecimalField(max_digits=15, decimal_places=4)
    high_price = models.DecimalField(max_digits=15, decimal_places=4)
    volume = models.DecimalField(max_digits=20, decimal_places=4, null=True)

    candle_datetime = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
