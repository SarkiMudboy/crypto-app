from abc import abstractmethod
from abc import ABC
from typing import Dict, Any, List
from crypto_app import settings
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

class CoinMarketCapAPIHandler(object):

    def __init__(self) -> None:
        
        self.enpoints = {
            'cryptocurrencies': 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/trending/latest'
        }

    def get_listings(self, parameters: Dict[str, str], **kwargs) -> Dict[str, Any]:
        
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': settings.env("PRO_API_KEY"),
        }

        url = self.enpoints.get('cryptocurrencies')

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

        return self.response(data)
    
    def response(self, coins: List[Dict[str, str]]) -> Dict[str, Any]:

        data = []
 
        for coin in coins["data"]:
            price_data = coin.get("qoute").get("USD")
            data.append({
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "price": price_data.get("price"),
                "percent_change_24h": price_data.get("percent_change_24h")
            })
        
        return data
