from celery import shared_task
from abstract.api.coin_api import CoinMarketCapAPIHandler
from crypto_app.wallets.handlers.wallet import WalletHandlerFactory

@shared_task()
def update_top_ten_ranked_cryptocurrencies() -> None:

    handler = CoinMarketCapAPIHandler()

    params = {
        'start':'1',
        'limit':'10',
        'convert':'USD'
    }
    coins = handler.get_listings(parameters=params)
    handler = WalletHandlerFactory.get("cryptocurrency")
    handler.update_coins(coins)
