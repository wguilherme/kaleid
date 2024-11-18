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
            if isinstance(self.config, dict) and 'sources' in self.config:
                for source in self.config['sources']:
                    if source['type'] == 'rss':
                        feed_url = source['url']
                        feed = feedparser.parse(feed_url)
                        logger.info(f"RSS feed fetched with {len(feed.entries)} entries")
                        return feed.entries
            else:
                feed = feedparser.parse(self.config['url'])
                return feed.entries
        except Exception as e:
            logger.error(f"RSS feed error: {str(e)}")
            return []

    def process(self, entries: List[Dict]) -> List[Dict]:

        logger.info(f"Processing {len(entries)} entries")

        if not entries:
            return []

        try:
            if isinstance(self.config, dict) and 'sources' in self.config:
                for source in self.config['sources']:
                    if source['type'] == 'rss':
                        source_url = source['url']
                        break
            else:
                source_url = self.config['url']
        except Exception as e:
            logger.error(f"Error getting source URL from config: {str(e)}")
            source_url = "unknown"

        # Processa o primeiro item separadamente para poder logar
        first_entry = entries[0]

        try:
            first_processed = {
                'type': 'news',
                'source': source_url,
                'title': getattr(first_entry, 'title', 'No title'),
                'description': getattr(first_entry, 'description', 'No description'),
                'link': getattr(first_entry, 'link', 'No link'),
                'pub_date': getattr(first_entry, 'published', 'No date'),
                'collected_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing first entry: {str(e)}")
            first_processed = None
        
        # logger.info(f"First processed entry: {first_processed}")

        return [{
            'type': 'news',
            'source': source_url,
            'title': entry.title,
            'description': self.clean_html(entry.description),
            'link': entry.link,
            'pub_date': entry.published,
            'collected_at': datetime.now().isoformat()
        } for entry in entries]