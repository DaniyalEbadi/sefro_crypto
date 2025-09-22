from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import OuterRef, Subquery
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import CryptoAsset, CryptoPrice
from .serializers import (
    CryptoPriceBasicSerializer, 
    CryptoPricePremiumSerializer,
    LatestPricesQuerySerializer,
    CryptoSymbolSerializer
)


# Create your views here.


@extend_schema(
    tags=['Crypto'],
    parameters=[
        OpenApiParameter(
            name='symbols',
            description='Comma-separated list of crypto symbols (e.g., BTC,ETH,ADA)',
            required=False,
            type=str
        )
    ],
    responses={
        200: CryptoPriceBasicSerializer(many=True),
        401: {'description': 'Authentication required'}
    },
    summary="Get latest crypto prices",
    description="Get latest cryptocurrency prices. Premium users get additional data like market cap, volume, etc."
)
class LatestPricesView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LatestPricesQuerySerializer

    def get(self, request):
        symbols_param = request.query_params.get('symbols', '')
        symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
        assets_qs = CryptoAsset.objects.all()
        if symbols:
            assets_qs = assets_qs.filter(symbol__in=symbols)
        latest_price_sub = CryptoPrice.objects.filter(asset=OuterRef('pk')).order_by('-last_updated')
        assets = assets_qs.annotate(
            latest_price_id=Subquery(latest_price_sub.values('id')[:1])
        )
        price_map = {p.asset_id: p for p in CryptoPrice.objects.filter(id__in=[a.latest_price_id for a in assets if a.latest_price_id])}
        is_premium = request.user.has_active_premium()
        data = []
        for asset in assets:
            price = price_map.get(asset.id)
            if not price:
                continue
            base = {
                'symbol': asset.symbol,
                'name': asset.name,
                'price_usd': float(price.price_usd),
                'change_24h_percent': float(price.change_24h_percent),
                'last_updated': price.last_updated.isoformat().replace('+00:00', 'Z'),
            }
            if is_premium:
                base.update({
                    'market_cap_usd': float(price.market_cap_usd) if price.market_cap_usd is not None else None,
                    'volume_24h_usd': float(price.volume_24h_usd) if price.volume_24h_usd is not None else None,
                    'circulating_supply': float(price.circulating_supply) if price.circulating_supply is not None else None,
                    'total_supply': float(price.total_supply) if price.total_supply is not None else None,
                    'ath': float(price.ath) if price.ath is not None else None,
                    'atl': float(price.atl) if price.atl is not None else None,
                    'logo_url': asset.logo_url,
                })
            data.append(base)
        return Response(data)


@extend_schema(
    tags=['Crypto'],
    responses={
        200: CryptoSymbolSerializer(many=True),
        401: {'description': 'Authentication required'}
    },
    summary="Get all available crypto symbols",
    description="Get a list of all available cryptocurrency symbols and their basic information."
)
class CryptoSymbolsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CryptoSymbolSerializer

    def get(self, request):
        assets = CryptoAsset.objects.all().order_by('symbol')
        data = []
        for asset in assets:
            data.append({
                'symbol': asset.symbol,
                'name': asset.name,
                'logo_url': asset.logo_url,
            })
        return Response(data)
