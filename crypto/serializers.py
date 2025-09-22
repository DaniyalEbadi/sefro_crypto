from rest_framework import serializers


class CryptoPriceBasicSerializer(serializers.Serializer):
    """Basic crypto price data for regular users"""
    symbol = serializers.CharField()
    name = serializers.CharField()
    price_usd = serializers.FloatField()
    change_24h_percent = serializers.FloatField()
    last_updated = serializers.CharField()


class CryptoPricePremiumSerializer(CryptoPriceBasicSerializer):
    """Extended crypto price data for premium users"""
    market_cap_usd = serializers.FloatField(allow_null=True)
    volume_24h_usd = serializers.FloatField(allow_null=True)
    circulating_supply = serializers.FloatField(allow_null=True)
    total_supply = serializers.FloatField(allow_null=True)
    ath = serializers.FloatField(allow_null=True)
    atl = serializers.FloatField(allow_null=True)
    logo_url = serializers.URLField(allow_null=True)


class CryptoSymbolSerializer(serializers.Serializer):
    """Crypto asset symbol data"""
    symbol = serializers.CharField()
    name = serializers.CharField()
    logo_url = serializers.URLField(allow_null=True)


class LatestPricesQuerySerializer(serializers.Serializer):
    """Query parameters for latest prices endpoint"""
    symbols = serializers.CharField(
        required=False,
        help_text="Comma-separated list of crypto symbols (e.g., BTC,ETH,ADA)"
    )