from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List
import html

class DataCleaner:
    @staticmethod
    def clean_html(text: str) -> str:
        """Remove HTML tags and clean text"""
        # Decode HTML entities first
        text = html.unescape(text)
        
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text
    
    @staticmethod
    def clean_rss_entry(entry: Dict[str, Any]) -> str:
        """Clean and format RSS entry data"""
        parts = []
        
        # Clean and add title
        if entry.get("title"):
            title = DataCleaner.clean_html(entry["title"])
            parts.append(f"Title: {title}")
        
        # Clean and add content
        content = ""
        if entry.get("content"):
            content = DataCleaner.clean_html(entry["content"])
        elif entry.get("summary"):
            content = DataCleaner.clean_html(entry["summary"])
        elif entry.get("description"):
            content = DataCleaner.clean_html(entry["description"])
        
        if content:
            parts.append(f"Content: {content}")
        
        # Add metadata
        if entry.get("published"):
            parts.append(f"Published: {entry['published']}")
        
        if entry.get("link"):
            parts.append(f"Source: {entry['link']}")
        
        return "\n".join(parts)
    
    @staticmethod
    def clean_api_data(data: Dict[str, Any], source: str) -> str:
        """Clean and format API data"""
        if source == "news":
            return DataCleaner._clean_news_api_data(data)
        elif source == "weather":
            return DataCleaner._clean_weather_api_data(data)
        return str(data)
    
    @staticmethod
    def _clean_news_api_data(data: Dict[str, Any]) -> str:
        """Clean news API data"""
        if "articles" not in data:
            return ""
        
        cleaned_articles = []
        for article in data["articles"]:
            parts = []
            
            # Clean and add title
            if article.get("title"):
                title = DataCleaner.clean_html(article["title"])
                parts.append(f"Title: {title}")
            
            # Clean and add description
            if article.get("description"):
                description = DataCleaner.clean_html(article["description"])
                parts.append(f"Description: {description}")
            
            # Clean and add content
            if article.get("content"):
                content = DataCleaner.clean_html(article["content"])
                parts.append(f"Content: {content}")
            
            # Add metadata
            if article.get("publishedAt"):
                parts.append(f"Published: {article['publishedAt']}")
            
            if article.get("url"):
                parts.append(f"Source: {article['url']}")
            
            cleaned_articles.append("\n".join(parts))
        
        return "\n\n".join(cleaned_articles)
    
    @staticmethod
    def _clean_weather_api_data(data: Dict[str, Any]) -> str:
        """Clean weather API data"""
        parts = []
        
        if "name" in data:
            parts.append(f"Location: {data['name']}")
        
        if "main" in data:
            main = data["main"]
            if "temp" in main:
                # Convert Kelvin to Celsius
                temp_c = main["temp"] - 273.15
                parts.append(f"Temperature: {temp_c:.1f}°C")
            if "humidity" in main:
                parts.append(f"Humidity: {main['humidity']}%")
            if "pressure" in main:
                parts.append(f"Pressure: {main['pressure']} hPa")
        
        if "weather" in data and data["weather"]:
            weather = data["weather"][0]
            if "description" in weather:
                description = weather["description"].capitalize()
                parts.append(f"Conditions: {description}")
        
        return "\n".join(parts)