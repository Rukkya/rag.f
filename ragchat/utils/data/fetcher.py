import feedparser
import aiohttp
from typing import Dict, Any, List
from datetime import datetime
import asyncio

class DataFetcher:
    def __init__(self):
        self.rss_feeds = {
            "tech": [],
            "science": [],
            "news": []
        }
    
    def add_rss_feed(self, category: str, url: str) -> bool:
        """Add a new RSS feed URL to a category"""
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                return False
            
            if category not in self.rss_feeds:
                self.rss_feeds[category] = []
            
            if url not in self.rss_feeds[category]:
                self.rss_feeds[category].append(url)
            return True
        except Exception as e:
            print(f"Error adding RSS feed: {str(e)}")
            return False
    
    async def fetch_rss_feed(self, url: str) -> List[Dict[str, Any]]:
        """Fetch and parse a single RSS feed"""
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"Warning: Feed {url} has format issues")
                return []
            
            entries = []
            for entry in feed.entries[:10]:
                content = ""
                if hasattr(entry, "content"):
                    content = entry.content[0].value
                elif hasattr(entry, "summary"):
                    content = entry.summary
                elif hasattr(entry, "description"):
                    content = entry.description
                
                published = None
                for date_field in ['published', 'updated', 'created']:
                    if hasattr(entry, date_field):
                        published = getattr(entry, date_field)
                        break
                
                entries.append({
                    "title": entry.title if hasattr(entry, "title") else "No Title",
                    "link": entry.link if hasattr(entry, "link") else "",
                    "published": published,
                    "content": content
                })
            
            return entries
        except Exception as e:
            print(f"Error fetching RSS feed {url}: {str(e)}")
            return []