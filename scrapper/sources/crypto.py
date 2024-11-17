# sources/crypto.py
from .base import DataSource
import requests
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class CryptoPrice(DataSource):
    def __init__(self, config: Dict = None):
        default_config = {
            'url': 'https://api.coingecko.com/api/v3/simple/price',
            'symbol': 'bitcoin',
            'params': {
                'ids': 'bitcoin',
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true'
            }
        }
        super().__init__(config or default_config)

    def fetch(self) -> List[Dict]:
        try:
            response = requests.get(
                self.config['url'],
                params=self.config['params']
            )
            response.raise_for_status()
            data = response.json()
            
            # Adapta o formato da resposta do CoinGecko
            crypto_id = self.config['params']['ids']
            if crypto_id in data:
                return [{
                    'price_usd': data[crypto_id]['usd'],
                    'market_cap_usd': data[crypto_id].get('usd_market_cap', 0),
                    'volume_24h': data[crypto_id].get('usd_24h_vol', 0),
                    'change_24h': data[crypto_id].get('usd_24h_change', 0)
                }]
            return []
        except Exception as e:
            logger.error(f"Crypto API error: {str(e)}")
            return []

    def process(self, data: List[Dict]) -> List[Dict]:
        results = []
        for item in data:
            try:
                price_data = {
                    'type': 'crypto_price',
                    'symbol': self.config['symbol'],
                    'price_usd': float(item['price_usd']),
                    'market_cap': float(item['market_cap_usd']),
                    'volume_24h': float(item['volume_24h']),
                    'change_24h': float(item['change_24h']),
                    'collected_at': datetime.now().isoformat()
                }
                results.append(price_data)
            except (KeyError, ValueError) as e:
                logger.error(f"Error processing crypto data: {str(e)}")
        return results