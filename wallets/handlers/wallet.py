from django.db.models import QuerySet
from ..models import Coin, Cryptocurrency, Wallet
from .abstract import Handler
from typing import Dict, Any, List, Tuple
from django.contrib.auth.models import AbstractBaseUser

class WalletHandlerFactory(object):

    @staticmethod
    def get(endpoint: str) -> Handler:
        
        endpoint_handlers = {
            "get_wallet": GetWalletHandler,
            "add_coin": AddCoinHandler,
            "remove_coin": RemoveCoinHandler,
            "cryptocurrency": CryptocurrencyHandler,
        }

        return endpoint_handlers[endpoint]()


class GetWalletHandler(Handler):

    def run(self, owner: AbstractBaseUser, **kwargs) -> Dict[str, Any]:
        error = self.validate(owner)
        if error:
            return None, error
        
        wallet = self.get_wallet(owner)
        coins = self.get_coins()

        return self.response(owner, wallet, coins)
    
    def validate(self, owner: AbstractBaseUser, **kwargs) -> Dict[str, Any]:
        return None

    def get_wallet(self, owner: AbstractBaseUser, **kwargs) -> Wallet:
        wallet = Wallet.objects.get(owner=owner)
        return wallet
    
    def get_coins(self):

        queryset = Cryptocurrency.objects.all()
        return queryset
    
    def response(self, owner: AbstractBaseUser, wallet: Wallet, coins: QuerySet) -> Dict[str, Any]:
        data = {
            "owner": owner,
            "wallet": wallet,
            "coins": []
        }

        for coin in coins:
            data["coins"].append(coin)

        return data, None
    

class AddCoinHandler(Handler):

    def run(self, owner: AbstractBaseUser, coin_id: str, amount: int, **kwargs) -> Dict[str, Any]:
        error = self.validate(owner)
        if error:
            return None, error
    
        wallet, coins = self.add_coin(owner, coin_id, amount)

        return self.response(owner, wallet, coins)
    
    def validate(self, owner: AbstractBaseUser, **kwargs) -> Dict[str, Any]:
        return None
    
    def add_coin(self, owner: AbstractBaseUser, coin_id: str, amount: int) -> Tuple[Wallet, Cryptocurrency]:

        wallet = Wallet.objects.get(owner=owner)

        crypto = Cryptocurrency.objects.get(id=coin_id)
        coin = Coin.objects.create(owner=owner, cryptocurrency=crypto, amount=amount)
        wallet.coins.add(coin)

        wallet.total_value += (crypto.current_price * float(amount))
        wallet.save()

        coins = Cryptocurrency.objects.all()
        return wallet, coins
    
    def response(self, owner: AbstractBaseUser, wallet: Wallet, coins: QuerySet) -> Dict[str, Any]:
        data = {
            "owner": owner,
            "wallet": wallet,
            "coins": []
        }

        for coin in coins:
            data["coins"].append(coin)

        return data, None


class RemoveCoinHandler(Handler):

    def run(self, owner: AbstractBaseUser, coin_id: str, **kwargs) -> Dict[str, Any]:
        error = self.validate(owner, coin_id)
        if error:
            return None, error
    
        wallet, coins = self.remove_coin(owner, coin_id)

        return self.response(owner, wallet, coins)
    
    def validate(self, owner: AbstractBaseUser, coin: str, **kwargs) -> Dict[str, Any]:
        return None
    
    def remove_coin(self, owner: AbstractBaseUser, coin_id: str) -> Tuple[Wallet, Cryptocurrency]:

        wallet = Wallet.objects.get(owner=owner)
        coin = Coin.objects.get(id=coin_id)
        for c in wallet.coins.all():
            if c.id == coin.id:
                wallet.coins.remove(c.id)
                wallet.total_value -= (float(c.amount) * c.cryptocurrency.current_price)

                c.delete()
                wallet.save()

        coins = Cryptocurrency.objects.all()
        return wallet, coins
    
    def response(self, owner: AbstractBaseUser, wallet: Wallet, coins: QuerySet) -> Dict[str, Any]:
        data = {
            "owner": owner,
            "wallet": wallet,
            "coins": []
        }

        for coin in coins:
            data["coins"].append(coin)

        return data, None


class CryptocurrencyHandler(Handler):
    
    def update_coins(self, coin_data: List[dict]) -> None:
        
        for coin in coin_data:
            crypto, created = Cryptocurrency.objects.get_or_create(name=coin_data.get("name"))

            if created:
                crypto.name = coin_data.get("name")
                crypto.symbol = coin_data.get("symbol")

            crypto.price = coin_data.get("price")
            crypto.percent_change_24h = coin_data.get("percent_change_24h")
            crypto.high_ranking = True
            crypto.save()




        