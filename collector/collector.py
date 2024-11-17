from sources.news import NewsRSSSource
from sources.crypto import CryptoPrice
from typing import Dict, Any
import logging
import json
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, config):
        self.sources = {
            # 'crypto': CryptoPrice(config),
            'news': NewsRSSSource(config)
        }

    def collect(self) -> Dict[str, Any]:
        collected_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'data': {}
        }

        for source_name, source in self.sources.items():
            try:
                logger.info(f"Collecting data from {source_name}")
                logger.debug(f"Config for {source_name}: {source.config}")
                collected_data['data'][source_name] = source.collect()

                logger.info(f"Data collected from {source_name}")
                logger.debug(f"Collected data for {source_name}: {collected_data['data'][source_name]}")
            except Exception as e:
                logger.error(f"Error collecting from {source_name}: {str(e)}")
                collected_data['data'][source_name] = []

        self._save_to_file(collected_data)
        return collected_data

    def _save_to_file(self, data: Dict[str, Any]) -> None:
        os.makedirs("output", exist_ok=True)
        filename = f"output/data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)