# sources/crypto.py
from .base import DataSource
import requests
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class CryptoPrice(DataSource):
    def fetch(self) -> List[Dict]:
        try:
            response = requests.get(self.config['url'])
            return [response.json()]
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