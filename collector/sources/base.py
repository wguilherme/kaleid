# sources/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import re
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

    @staticmethod
    def clean_html(html_content: str) -> str:
        """Remove HTML tags and clean up text content."""
        if not html_content:
            return ''
        
        try:
            # Remove HTML tags
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            logger.error(f"Error cleaning HTML content: {str(e)}")
            return html_content

    @staticmethod
    def clean_and_truncate(html_content: str, max_length: int = 500) -> str:
        """Clean HTML and truncate to specified length."""
        clean_text = DataSource.clean_html(html_content)
        if len(clean_text) > max_length:
            return clean_text[:max_length] + '...'
        return clean_text


    def collect(self) -> List[Dict]:
        """Main method to fetch and process data"""
        # self.logger.info(f"Collecting data from {self.__class__.__name__}")
        raw_data = self.fetch()
        # self.logger.info(f"Data collected from {raw_data}")

        if not raw_data:
            self.logger.warning("No data fetched")
            return []
        
        self.logger.info(f"Processing data from {self.__class__.__name__}")
        processed_data = self.process(raw_data)
        self.logger.info(f"Data processed from {processed_data}")

        if not processed_data:
            self.logger.warning("No data processed")
            return []
        
        return processed_data