from django.urls import path
from .views import WalletView

app_name: str = 'wallets'

get_wallet =  WalletView.as_view({"get": "get_wallet"})
add_coin = WalletView.as_view({"post": "add_coin"})
remove_coin = WalletView.as_view({"get": "remove_coin"})

urlpatterns = [
    path('get-wallet/', get_wallet, name="get-wallet"),
    path("get-wallet/<str:coin_id>", add_coin, name="add-coin"),
    path("get-wallet/remove/<str:coin_id>", remove_coin, name="remove-coin"),
]