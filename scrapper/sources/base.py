# sources/base.py
from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataSource(ABC):
    def __init__(self, config: Dict):
        self.config = config
    
    @abstractmethod
    def fetch(self) -> List[Dict]:
        pass

    @abstractmethod
    def process(self, data: List[Dict]) -> List[Dict]:
        pass
    
    def execute(self) -> List[Dict]:
        try:
            raw_data = self.fetch()
            processed_data = self.process(raw_data)
            return processed_data
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
            return []