from django.db import models
from django.utils import timezone


class CryptoAsset(models.Model):
    symbol = models.CharField(max_length=16, unique=True)  # e.g., BTC
    name = models.CharField(max_length=64)  # e.g., Bitcoin
    external_id = models.CharField(max_length=128, unique=True)  # provider id, e.g., coingecko 'bitcoin'
    logo_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class CryptoPrice(models.Model):
    asset = models.ForeignKey(CryptoAsset, on_delete=models.CASCADE, related_name='prices')
    price_usd = models.DecimalField(max_digits=24, decimal_places=8)
    change_24h_percent = models.DecimalField(max_digits=10, decimal_places=4)
    market_cap_usd = models.DecimalField(max_digits=28, decimal_places=2, null=True, blank=True)
    volume_24h_usd = models.DecimalField(max_digits=28, decimal_places=2, null=True, blank=True)
    circulating_supply = models.DecimalField(max_digits=28, decimal_places=8, null=True, blank=True)
    total_supply = models.DecimalField(max_digits=28, decimal_places=8, null=True, blank=True)
    ath = models.DecimalField(max_digits=28, decimal_places=8, null=True, blank=True)
    atl = models.DecimalField(max_digits=28, decimal_places=8, null=True, blank=True)
    last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        get_latest_by = 'last_updated'
        indexes = [
            models.Index(fields=['asset', 'last_updated']),
        ]

    def __str__(self):
        return f"{self.asset.symbol} @ {self.price_usd} ({self.last_updated.isoformat()})"
