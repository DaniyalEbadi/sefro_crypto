from django.urls import path
from . import views

urlpatterns = [
    path('prices/latest/', views.LatestPricesView.as_view(), name='crypto-latest-prices'),
    path('symbols/', views.CryptoSymbolsView.as_view(), name='crypto-symbols'),
] 