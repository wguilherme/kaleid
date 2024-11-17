# sources/stocks.py
from .base import DataSource
import requests
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class StockPrice(DataSource):
    def fetch(self) -> List[Dict]:
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': self.config['symbol'],
                'apikey': self.config['api_key']
            }
            response = requests.get(self.config['url'], params=params)
            return [response.json()]
        except Exception as e:
            logger.error(f"Stock API error: {str(e)}")
            return []

    def process(self, data: List[Dict]) -> List[Dict]:
        results = []
        for item in data:
            try:
                quote = item['Global Quote']
                price_data = {
                    'type': 'stock_price',
                    'symbol': self.config['symbol'],
                    'price': float(quote['05. price']),
                    'volume': int(quote['06. volume']),
                    'change_percent': quote['10. change percent'].rstrip('%'),
                    'collected_at': datetime.now().isoformat()
                }
                results.append(price_data)
            except (KeyError, ValueError) as e:
                logger.error(f"Error processing stock data: {str(e)}")
        return results