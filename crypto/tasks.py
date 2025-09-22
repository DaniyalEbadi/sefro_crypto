import os
import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import CryptoAsset, CryptoPrice


def coingecko_fetch(ids_csv: str):
    url = f"{settings.CRYPTO_API_URL}/coins/markets"
    params = {
        'vs_currency': 'usd',
        'ids': ids_csv,
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': '24h',
    }
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


@shared_task
def fetch_and_broadcast_prices():
    assets = list(CryptoAsset.objects.all())
    if not assets:
        return
    ids_csv = ','.join([a.external_id for a in assets])
    data = coingecko_fetch(ids_csv)
    now = timezone.now()
    created = []
    for item in data:
        symbol = (item.get('symbol') or '').upper()
        ext_id = item.get('id')
        name = item.get('name')
        try:
            asset = next(a for a in assets if a.external_id == ext_id)
        except StopIteration:
            asset, _ = CryptoAsset.objects.get_or_create(external_id=ext_id, defaults={
                'symbol': symbol,
                'name': name,
                'logo_url': (item.get('image') or ''),
            })
        price = CryptoPrice.objects.create(
            asset=asset,
            price_usd=item.get('current_price') or 0,
            change_24h_percent=(item.get('price_change_percentage_24h') or 0),
            market_cap_usd=item.get('market_cap'),
            volume_24h_usd=item.get('total_volume'),
            circulating_supply=item.get('circulating_supply'),
            total_supply=item.get('total_supply'),
            ath=item.get('ath'),
            atl=item.get('atl'),
            last_updated=now,
        )
        created.append(price)
        payload = {
            'symbol': asset.symbol,
            'name': asset.name,
            'price_usd': float(price.price_usd),
            'change_24h_percent': float(price.change_24h_percent),
            'last_updated': price.last_updated.isoformat().replace('+00:00', 'Z'),
            'market_cap_usd': float(price.market_cap_usd) if price.market_cap_usd is not None else None,
            'volume_24h_usd': float(price.volume_24h_usd) if price.volume_24h_usd is not None else None,
            'circulating_supply': float(price.circulating_supply) if price.circulating_supply is not None else None,
            'total_supply': float(price.total_supply) if price.total_supply is not None else None,
            'ath': float(price.ath) if price.ath is not None else None,
            'atl': float(price.atl) if price.atl is not None else None,
            'logo_url': asset.logo_url,
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'crypto_{asset.symbol.upper()}', {
            'type': 'price.update',
            'data': payload,
        })
    return len(created) 