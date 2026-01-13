"""
Agent: Article Ranking Agent
Uses LLM to select the best trending article from fetched articles.
"""

import logging
import yaml
from typing import Dict, List, Any, Optional

from groq import Groq

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb import MongoDBManager

logger = logging.getLogger(__name__)


class ArticleRankingAgent:
    """
    Article Ranking Agent that uses LLM to select the best trending news.
    
    When enabled, analyzes all raw articles and keeps only the top N,
    marking the rest as 'filtered' so they won't be processed.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the article ranking agent.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.db = self._init_database()
        self.llm = self._init_llm()
        
        # Ranking settings
        ranking_config = self.config.get("ARTICLE_RANKING", {})
        self.enabled = ranking_config.get("ENABLED", True)
        self.top_n = ranking_config.get("TOP_N", 1)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
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
    
    def _init_llm(self) -> Groq:
        """Initialize Groq LLM client."""
        llm_config = self.config.get("LLM", {})
        api_key = llm_config.get("API_KEY")
        if not api_key:
            raise ValueError("LLM API_KEY not found in config")
        return Groq(api_key=api_key)
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Make a call to the Groq LLM."""
        llm_config = self.config.get("LLM", {})
        model = llm_config.get("MODEL", "llama-3.3-70b-versatile")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.llm.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,  # Lower temp for more consistent ranking
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def rank_articles(self, articles: List[Dict]) -> Optional[int]:
        """
        Use LLM to rank articles and return the index of the best one.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Index of the best article (0-based), or None if failed
        """
        if not articles:
            return None
        
        if len(articles) == 1:
            return 0  # Only one article, it's the best by default
        
        # Build the prompt with article summaries
        articles_text = ""
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            description = article.get("description", "No description")
            source = article.get("source", "Unknown")
            articles_text += f"\n{i}. [{source}] {title}\n   {description}\n"
        
        system_prompt = """You are a news editor selecting the most newsworthy article.
Consider: breaking news value, global impact, reader interest, and timeliness.
Respond with ONLY the number of the best article (e.g., "1" or "2"). Nothing else."""
        
        prompt = f"""Which of these articles is the MOST trending/newsworthy right now?
{articles_text}
Reply with just the number (1-{len(articles)}):"""
        
        try:
            response = self._call_llm(prompt, system_prompt)
            # Parse the response - expect a single number
            choice = int(response.strip().replace(".", "").split()[0])
            if 1 <= choice <= len(articles):
                logger.info(f"LLM selected article #{choice} as most trending")
                return choice - 1  # Convert to 0-based index
            else:
                logger.warning(f"LLM returned invalid choice: {choice}")
                return 0  # Default to first article
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse LLM response '{response}': {e}")
            return 0  # Default to first article
    
    def run(self) -> Dict[str, Any]:
        """
        Run the article ranking agent.
        
        Fetches raw articles, ranks them with LLM, and marks non-selected
        articles as 'filtered' so they won't be processed.
        
        Returns:
            Summary of ranking operation
        """
        result = {
            "enabled": self.enabled,
            "total_raw": 0,
            "selected": 0,
            "filtered": 0
        }
        
        # Check if ranking is enabled
        if not self.enabled:
            logger.info("Article ranking is DISABLED - all articles will be processed")
            return result
        
        logger.info(f"Article ranking is ENABLED - selecting top {self.top_n} article(s)")
        
        # Get all raw articles
        raw_articles = self.db.get_raw_articles(limit=100)
        result["total_raw"] = len(raw_articles)
        
        if not raw_articles:
            logger.info("No raw articles to rank")
            return result
        
        if len(raw_articles) <= self.top_n:
            logger.info(f"Only {len(raw_articles)} articles, no filtering needed")
            result["selected"] = len(raw_articles)
            return result
        
        # Rank articles using LLM
        logger.info(f"Ranking {len(raw_articles)} articles to select top {self.top_n}")
        best_index = self.rank_articles(raw_articles)
        
        if best_index is None:
            logger.warning("Ranking failed, keeping all articles")
            result["selected"] = len(raw_articles)
            return result
        
        # Mark non-selected articles as 'filtered'
        from bson import ObjectId
        for i, article in enumerate(raw_articles):
            article_id = str(article["_id"])
            if i == best_index:
                logger.info(f"SELECTED: {article.get('title', 'Unknown')[:60]}...")
                result["selected"] += 1
            else:
                # Mark as filtered so it won't be processed
                self.db.update_article_status(article_id, "filtered")
                logger.debug(f"FILTERED: {article.get('title', 'Unknown')[:60]}...")
                result["filtered"] += 1
        
        logger.info(f"Ranking complete: {result['selected']} selected, {result['filtered']} filtered")
        return result
    
    def close(self):
        """Clean up resources."""
        if self.db:
            self.db.disconnect()


# For running as a standalone script
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("\n" + "="*60)
    print("  ARTICLE RANKING AGENT - Test Run")
    print("="*60)
    
    try:
        agent = ArticleRankingAgent()
        result = agent.run()
        
        print(f"\n  Enabled:  {result['enabled']}")
        print(f"  Raw:      {result['total_raw']}")
        print(f"  Selected: {result['selected']}")
        print(f"  Filtered: {result['filtered']}")
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'agent' in locals():
            agent.close()
