# sources/news.py
from .base import DataSource
import feedparser
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

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