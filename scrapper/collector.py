# collector.py
from sources.news import NewsRSSSource
from sources.crypto import CryptoPrice
from sources.stocks import StockPrice
from processors.gpt import GPTProcessor
from typing import Dict, List
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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
        source_mapping = {
            'rss': NewsRSSSource,
            'crypto': CryptoPrice,
            'stock': StockPrice
        }
        
        for source_config in self.config['sources']:
            source_type = source_config['type']
            if source_type in source_mapping:
                sources.append(source_mapping[source_type](source_config))
            else:
                logger.warning(f"Unknown source type: {source_type}")
                
        return sources
    
    def collect(self) -> List[Dict]:
        all_data = []
        
        for source in self.sources:
            data = source.execute()
            processed_data = [
                self.gpt.process(item) for item in data
            ]
            all_data.extend(processed_data)
            
        return all_data