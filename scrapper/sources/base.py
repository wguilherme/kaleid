# sources/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging

class DataSource(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def fetch(self) -> List[Dict]:
        """Fetches raw data from the source"""
        pass

    @abstractmethod
    def process(self, data: List[Dict]) -> List[Dict]:
        """Processes the raw data into standardized format"""
        pass

    def collect(self) -> List[Dict]:
        """Main method to fetch and process data"""
        raw_data = self.fetch()
        if not raw_data:
            self.logger.warning("No data fetched")
            return []
        return self.process(raw_data)