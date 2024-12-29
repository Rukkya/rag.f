import feedparser
import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import asyncio
import aiohttp
from bs4 import BeautifulSoup

class DataFetcher:
    def __init__(self):
        # Initialize with empty feed lists that can be updated
        self.rss_feeds = {
            "tech": [],
            "science": [],
            "news": []
        }
        
        self.apis = {
            "news": "https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_API_KEY",
            "weather": "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"
        }
    
    def add_rss_feed(self, category: str, url: str) -> bool:
        """Add a new RSS feed URL to a category"""
        try:
            # Validate the feed URL
            feed = feedparser.parse(url)
            if feed.bozo:  # feedparser sets bozo to 1 if there's an error
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
            for entry in feed.entries[:10]:  # Limit to 10 most recent entries
                content = ""
                if hasattr(entry, "content"):
                    content = entry.content[0].value
                elif hasattr(entry, "summary"):
                    content = entry.summary
                elif hasattr(entry, "description"):
                    content = entry.description
                
                # Extract publish date with fallbacks
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
    
    async def fetch_api_endpoint(self, name: str, url: str) -> Dict[str, Any]:
        """Fetch data from an API endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    print(f"API {name} returned status code {response.status}")
                    return {}
        except Exception as e:
            print(f"Error fetching API {name}: {str(e)}")
            return {}
    
    async def fetch_all_data(self) -> Dict[str, Any]:
        """Fetch all RSS feeds and API data concurrently"""
        all_data = {
            "rss": {},
            "api": {}
        }
        
        # Fetch RSS feeds
        for category, feeds in self.rss_feeds.items():
            if feeds:  # Only process if there are feeds in the category
                feed_tasks = [self.fetch_rss_feed(url) for url in feeds]
                results = await asyncio.gather(*feed_tasks)
                # Flatten and filter out empty results
                category_entries = [
                    entry for sublist in results 
                    for entry in sublist if entry
                ]
                if category_entries:
                    all_data["rss"][category] = category_entries
        
        # Fetch API data
        api_tasks = [
            self.fetch_api_endpoint(name, url) 
            for name, url in self.apis.items()
        ]
        api_results = await asyncio.gather(*api_tasks)
        all_data["api"] = {
            name: result 
            for name, result in zip(self.apis.keys(), api_results)
            if result  # Only include non-empty results
        }
        
        return all_data