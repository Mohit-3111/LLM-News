"""
Agent 1: Scraper & Ingestion Agent
Fetches news from NewsAPI and GNews, extracts full content, and stores in MongoDB.
"""

import logging
import requests
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb import MongoDBManager
from utils.helpers import extract_article_text, parse_datetime

logger = logging.getLogger(__name__)


class ScraperAgent:
    """
    Scraper agent that fetches news from multiple sources and stores in MongoDB.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the scraper agent with configuration.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.db = self._init_database()
        
        # API configurations
        self.newsapi_key = self.config["NEWS_API_ORG"]["API_KEY"]
        self.gnews_key = self.config["GOOGLE_NEWS"]["API_KEY"]
        self.user_agent = self.config["SCRAPER"]["USER_AGENT"]
        self.timeout = self.config["SCRAPER"]["REQUEST_TIMEOUT"]
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def _init_database(self) -> MongoDBManager:
        """Initialize MongoDB connection."""
        mongo_config = self.config["MONGODB"]
        db = MongoDBManager(
            connection_url=mongo_config["CONNECTION_URL"],
            database_name=mongo_config["DATABASE_NAME"],
            collection_name=mongo_config["COLLECTION_NAME"]
        )
        if not db.connect():
            raise ConnectionError("Failed to connect to MongoDB")
        return db
    
    def fetch_newsapi(self, source: str = "bbc-news") -> List[Dict[str, Any]]:
        """
        Fetch articles from NewsAPI by source.
        
        Args:
            source: News source identifier (default: bbc-news)
            
        Returns:
            List of article dictionaries
        """
        articles = []
        url = f"https://newsapi.org/v2/top-headlines?sources={source}&language=en"
        headers = {"Authorization": f"Bearer {self.newsapi_key}"}
        
        try:
            logger.info(f"Fetching articles from NewsAPI (source: {source})")
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return articles
            
            for item in data.get("articles", []):
                article = self._process_article(item, "NewsAPI")
                if article:
                    articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from NewsAPI")
            return articles
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"NewsAPI HTTP error: {e}")
            return articles
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI request error: {e}")
            return articles
        except Exception as e:
            logger.error(f"Unexpected error fetching from NewsAPI: {e}")
            return articles
    
    def fetch_trending_newsapi(self, category: str = "technology") -> List[Dict[str, Any]]:
        """
        Fetch trending/latest articles from NewsAPI by category.
        This gets the most current top headlines across all sources.
        
        Args:
            category: News category (business, entertainment, general, health, 
                     science, sports, technology)
            
        Returns:
            List of article dictionaries
        """
        articles = []
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "category": category,
            "language": "en",
            "pageSize": 20,  # Get more to have diversity options
            "country": "us"  # Top headlines require country or source
        }
        headers = {"Authorization": f"Bearer {self.newsapi_key}"}
        
        try:
            logger.info(f"Fetching trending articles from NewsAPI (category: {category})")
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return articles
            
            for item in data.get("articles", []):
                article = self._process_article(item, "NewsAPI")
                if article:
                    articles.append(article)
            
            logger.info(f"Fetched {len(articles)} trending articles from NewsAPI ({category})")
            return articles
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"NewsAPI HTTP error: {e}")
            return articles
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI request error: {e}")
            return articles
        except Exception as e:
            logger.error(f"Unexpected error fetching trending from NewsAPI: {e}")
            return articles
    
    def fetch_gnews(self, category: str = "general", max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch articles from GNews.
        
        Args:
            category: News category (default: general)
            max_articles: Maximum number of articles (free tier: 10)
            
        Returns:
            List of article dictionaries
        """
        articles = []
        url = "https://gnews.io/api/v4/top-headlines"
        params = {
            "category": category,
            "lang": "en",
            "max": max_articles,
            "apikey": self.gnews_key
        }
        
        try:
            logger.info(f"Fetching articles from GNews (category: {category})")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("articles", []):
                article = self._process_article(item, "GNews")
                if article:
                    articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from GNews")
            return articles
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"GNews HTTP error: {e}")
            return articles
        except requests.exceptions.RequestException as e:
            logger.error(f"GNews request error: {e}")
            return articles
        except Exception as e:
            logger.error(f"Unexpected error fetching from GNews: {e}")
            return articles
    
    def _process_article(self, raw_article: Dict[str, Any], api_source: str) -> Optional[Dict[str, Any]]:
        """
        Process a raw article from an API, extracting full content.
        
        Args:
            raw_article: Raw article data from API
            api_source: Name of the API source
            
        Returns:
            Processed article dictionary or None if failed
        """
        url = raw_article.get("url")
        if not url:
            return None
        
        # Extract full article content
        content = extract_article_text(url, self.user_agent, self.timeout)
        if not content:
            logger.debug(f"Could not extract content from: {url}")
            return None
        
        # Build article object
        article = {
            "source": raw_article.get("source", {}).get("name", "Unknown"),
            "apiSource": api_source,
            "title": raw_article.get("title", ""),
            "description": raw_article.get("description", ""),
            "url": url,
            "imageUrl": raw_article.get("urlToImage") or raw_article.get("image", ""),
            "publishedAt": raw_article.get("publishedAt", ""),
            "content": content,
            "fetchedAt": datetime.utcnow().isoformat()
        }
        
        return article
    
    def _select_diverse_articles(self, articles: List[Dict[str, Any]], max_count: int = 5) -> List[Dict[str, Any]]:
        """
        Select articles ensuring each one is from a different source.
        
        Args:
            articles: List of all fetched articles
            max_count: Maximum number of articles to return (default: 5)
            
        Returns:
            List of articles with unique sources
        """
        seen_sources = set()
        diverse_articles = []
        
        for article in articles:
            source = article.get("source", "").lower()
            if source and source not in seen_sources:
                seen_sources.add(source)
                diverse_articles.append(article)
                logger.debug(f"Selected article from source: {article.get('source')}")
                
                if len(diverse_articles) >= max_count:
                    break
        
        logger.info(f"Selected {len(diverse_articles)} articles from {len(seen_sources)} unique sources")
        return diverse_articles
    
    def run(self, newsapi_count: int = 5, gnews_count: int = 2, use_trending: bool = True) -> Dict[str, Any]:
        """
        Run the scraper agent - fetch trending news from diverse sources.
        
        Args:
            newsapi_count: Number of articles from NewsAPI (default: 5)
            gnews_count: Number of articles from GNews (default: 2)
            use_trending: If True, fetch trending news by category (more current)
            
        Returns:
            Summary of the scraping operation
        """
        newsapi_articles = []
        gnews_articles = []
        summary = {
            "startTime": datetime.utcnow().isoformat(),
            "sources": {},
            "totalFetched": 0,
            "uniqueSelected": 0,
            "inserted": 0,
            "duplicates": 0,
            "errors": 0
        }
        
        seen_sources = set()
        
        # Strategy 1: Fetch trending news by category (more current/latest)
        if use_trending:
            trending_categories = ["technology", "business", "science", "general"]
            
            for category in trending_categories:
                if len(newsapi_articles) >= newsapi_count:
                    break
                try:
                    articles = self.fetch_trending_newsapi(category)
                    for article in articles:
                        if len(newsapi_articles) >= newsapi_count:
                            break
                        source_name = article.get("source", "").lower()
                        if source_name and source_name not in seen_sources:
                            seen_sources.add(source_name)
                            newsapi_articles.append(article)
                            summary["sources"][f"newsapi_{category}"] = summary["sources"].get(f"newsapi_{category}", 0) + 1
                            logger.info(f"Added trending article from {article.get('source')}")
                except Exception as e:
                    logger.error(f"Error fetching trending from NewsAPI ({category}): {e}")
            
            logger.info(f"NewsAPI trending: Got {len(newsapi_articles)} articles from {len(seen_sources)} unique sources")
        
        # Strategy 2: Fallback to source-based fetching if needed
        if len(newsapi_articles) < newsapi_count:
            newsapi_sources = [
                "bbc-news", "cnn", "reuters", "the-verge",
                "techcrunch", "abc-news", "associated-press", "bloomberg"
            ]
            
            for source in newsapi_sources:
                if len(newsapi_articles) >= newsapi_count:
                    break
                try:
                    articles = self.fetch_newsapi(source)
                    if articles:
                        article = articles[0]
                        source_name = article.get("source", "").lower()
                        if source_name not in seen_sources:
                            seen_sources.add(source_name)
                            newsapi_articles.append(article)
                            summary["sources"][f"newsapi_{source}"] = 1
                            logger.info(f"Added 1 article from NewsAPI: {article.get('source')}")
                except Exception as e:
                    logger.error(f"Error fetching from NewsAPI ({source}): {e}")
                    summary["sources"][f"newsapi_{source}"] = 0
            
            logger.info(f"NewsAPI: Got {len(newsapi_articles)} articles from {len(seen_sources)} unique sources")
        
        # Fetch from GNews (2 articles from different sources)
        try:
            all_gnews = self.fetch_gnews(max_articles=10)
            summary["sources"]["gnews_fetched"] = len(all_gnews)
            
            # Select articles from sources we haven't used yet
            for article in all_gnews:
                if len(gnews_articles) >= gnews_count:
                    break
                source_name = article.get("source", "").lower()
                if source_name and source_name not in seen_sources:
                    seen_sources.add(source_name)
                    gnews_articles.append(article)
                    logger.info(f"Added 1 article from GNews: {article.get('source')}")
            
            summary["sources"]["gnews_selected"] = len(gnews_articles)
            logger.info(f"GNews: Selected {len(gnews_articles)} articles")
        except Exception as e:
            logger.error(f"Error fetching from GNews: {e}")
            summary["sources"]["gnews"] = 0
        
        # Combine all articles
        all_articles = newsapi_articles + gnews_articles
        summary["totalFetched"] = len(all_articles)
        summary["uniqueSelected"] = len(all_articles)
        
        # Log selected sources
        if all_articles:
            sources = [a.get("source") for a in all_articles]
            logger.info(f"Final selected sources ({len(sources)}): {sources}")
        
        # Store in database
        if all_articles:
            results = self.db.insert_articles(all_articles)
            summary["inserted"] = results["inserted"]
            summary["duplicates"] = results["duplicates"]
            summary["errors"] = results["errors"]
        
        summary["endTime"] = datetime.utcnow().isoformat()
        
        # Log summary
        logger.info(f"Scraper run complete: {len(newsapi_articles)} from NewsAPI + {len(gnews_articles)} from GNews = "
                   f"{summary['totalFetched']} total, {summary['inserted']} new, {summary['duplicates']} duplicates")
        
        return summary
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return self.db.get_article_count()
    
    def close(self):
        """Clean up resources."""
        if self.db:
            self.db.disconnect()


# For running as a standalone script
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    agent = ScraperAgent()
    try:
        result = agent.run()
        print("\n" + "="*50)
        print("SCRAPER AGENT RUN COMPLETE")
        print("="*50)
        print(f"Total fetched: {result['totalFetched']}")
        print(f"New articles:  {result['inserted']}")
        print(f"Duplicates:    {result['duplicates']}")
        print(f"Errors:        {result['errors']}")
        print("="*50)
        
        stats = agent.get_stats()
        print("\nDatabase Statistics:")
        for status, count in stats.items():
            print(f"  {status}: {count}")
    finally:
        agent.close()
