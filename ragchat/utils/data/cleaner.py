from bs4 import BeautifulSoup
import re
import html
from typing import Dict, Any

class DataCleaner:
    @staticmethod
    def clean_html(text: str) -> str:
        """Remove HTML tags and clean text"""
        text = html.unescape(text)
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text
    
    @staticmethod
    def clean_rss_entry(entry: Dict[str, Any]) -> str:
        """Clean and format RSS entry data"""
        parts = []
        
        if entry.get("title"):
            title = DataCleaner.clean_html(entry["title"])
            parts.append(f"Title: {title}")
        
        content = ""
        if entry.get("content"):
            content = DataCleaner.clean_html(entry["content"])
        elif entry.get("summary"):
            content = DataCleaner.clean_html(entry["summary"])
        elif entry.get("description"):
            content = DataCleaner.clean_html(entry["description"])
        
        if content:
            parts.append(f"Content: {content}")
        
        if entry.get("published"):
            parts.append(f"Published: {entry['published']}")
        
        if entry.get("link"):
            parts.append(f"Source: {entry['link']}")
        
        return "\n".join(parts)