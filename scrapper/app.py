# scraper.py
import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime
import feedparser
import json
import logging
import sys
import os
from abc import ABC, abstractmethod
from openai import OpenAI
from typing import Dict, List
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataSource(ABC):
    def __init__(self, config: Dict):
        self.config = config
    
    @abstractmethod
    def fetch(self) -> List[Dict]:
        """Fetch and return data from source"""
        pass

    @abstractmethod
    def process(self, data: List[Dict]) -> List[Dict]:
        """Process fetched data"""
        pass
    
    def execute(self) -> List[Dict]:
        """Template method that defines the scraping algorithm"""
        try:
            raw_data = self.fetch()
            processed_data = self.process(raw_data)
            return processed_data
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
            return []

class NewsRSSSource(DataSource):
    def fetch(self) -> List[Dict]:
        try:
            feed = feedparser.parse(self.config['url'])
            return feed.entries
        except Exception as e:
            logger.error(f"RSS feed error {self.config['url']}: {str(e)}")
            return []

    def process(self, entries: List[Dict]) -> List[Dict]:
        return [{
            'type': 'news',
            'source': self.config['url'],
            'title': entry.title,
            'description': entry.description,
            'link': entry.link,
            'pub_date': entry.published,
            'collected_at': datetime.now().isoformat()
        } for entry in entries]

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

class StockPrice(DataSource):
    def fetch(self) -> List[Dict]:
        try:
            # Example using Alpha Vantage API
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

class GPTProcessor:
    def __init__(self, api_key: str, system_prompt: str):
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = system_prompt
    
    def process(self, data: Dict) -> Dict:
        if data['type'] != 'news':
            return data
            
        try:
            user_content = f"""Title: {data['title']}
Content: {data['description']}

Summarize this news article in 2-3 sentences. Then provide:
1. Main topic (1-3 words)
2. Key entities mentioned
3. Sentiment (positive/neutral/negative)"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7
            )
            
            data['gpt_analysis'] = {
                'summary': response.choices[0].message.content,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"GPT processing error: {str(e)}")
            data['gpt_analysis'] = {
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
            
        return data

class DataCollector:
    def __init__(self, config: Dict):
        self.config = config
        self.sources = self._init_sources()
        self.gpt = GPTProcessor(
            api_key=config['gpt_api_key'],
            system_prompt=config['gpt_system_prompt']
        )
    
    def _init_sources(self) -> List[DataSource]:
        sources = []
        
        # Initialize each source based on config
        for source_config in self.config['sources']:
            source_type = source_config['type']
            if source_type == 'rss':
                sources.append(NewsRSSSource(source_config))
            elif source_type == 'crypto':
                sources.append(CryptoPrice(source_config))
            elif source_type == 'stock':
                sources.append(StockPrice(source_config))
                
        return sources
    
    def collect(self) -> List[Dict]:
        all_data = []
        
        for source in self.sources:
            data = source.execute()
            
            # Apply GPT processing if needed
            processed_data = [
                self.gpt.process(item) for item in data
            ]
            
            all_data.extend(processed_data)
            
        return all_data

def run_collector():
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Initialize and run collector
        collector = DataCollector(config)
        data = collector.collect()
        
        # Save results
        output_file = f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data collection completed. Results saved to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_collector()
    sys.exit(0 if success else 1)