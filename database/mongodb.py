"""
MongoDB Database Connection Manager
Handles connection pooling and CRUD operations for articles.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Manages MongoDB connections and article operations."""
    
    def __init__(self, connection_url: str, database_name: str, collection_name: str):
        """
        Initialize MongoDB connection.
        
        Args:
            connection_url: MongoDB connection string
            database_name: Name of the database
            collection_name: Name of the collection for articles
        """
        self.connection_url = connection_url
        self.database_name = database_name
        self.collection_name = collection_name
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None
        
    def connect(self) -> bool:
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(self.connection_url)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # Create unique index on URL to prevent duplicates
            self.collection.create_index("url", unique=True)
            
            logger.info(f"Connected to MongoDB database: {self.database_name}")
            return True
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def insert_article(self, article: Dict[str, Any]) -> bool:
        """
        Insert a single article into the database.
        
        Args:
            article: Article dictionary with source, title, url, publishedAt, content, etc.
            
        Returns:
            True if inserted successfully, False if duplicate or error
        """
        try:
            # Add metadata
            article['createdAt'] = datetime.utcnow()
            article['status'] = 'raw'  # raw -> processed -> published
            
            self.collection.insert_one(article)
            logger.debug(f"Inserted article: {article.get('title', 'Unknown')[:50]}")
            return True
        except DuplicateKeyError:
            logger.debug(f"Duplicate article skipped: {article.get('url', 'Unknown')}")
            return False
        except PyMongoError as e:
            logger.error(f"Failed to insert article: {e}")
            return False
    
    def insert_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Insert multiple articles, skipping duplicates.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Dictionary with counts: {'inserted': n, 'duplicates': m, 'errors': k}
        """
        results = {'inserted': 0, 'duplicates': 0, 'errors': 0}
        
        for article in articles:
            try:
                article['createdAt'] = datetime.utcnow()
                article['status'] = 'raw'
                self.collection.insert_one(article)
                results['inserted'] += 1
            except DuplicateKeyError:
                results['duplicates'] += 1
            except PyMongoError:
                results['errors'] += 1
        
        logger.info(f"Insert results - New: {results['inserted']}, Duplicates: {results['duplicates']}, Errors: {results['errors']}")
        return results
    
    def get_raw_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get articles with 'raw' status for processing."""
        try:
            articles = list(self.collection.find({'status': 'raw'}).limit(limit))
            return articles
        except PyMongoError as e:
            logger.error(f"Failed to fetch raw articles: {e}")
            return []
    
    def update_article_status(self, article_id: str, new_status: str) -> bool:
        """Update the status of an article."""
        try:
            from bson import ObjectId
            result = self.collection.update_one(
                {'_id': ObjectId(article_id)},
                {'$set': {'status': new_status, 'updatedAt': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Failed to update article status: {e}")
            return False
    
    def get_article_count(self) -> Dict[str, int]:
        """Get count of articles by status."""
        try:
            pipeline = [
                {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
            ]
            results = list(self.collection.aggregate(pipeline))
            return {r['_id']: r['count'] for r in results}
        except PyMongoError as e:
            logger.error(f"Failed to get article count: {e}")
            return {}
    
    def update_article_curated_content(self, article_id: str, curated_data: Dict[str, Any]) -> bool:
        """
        Update an article with LLM-generated curated content.
        
        Args:
            article_id: MongoDB ObjectId string
            curated_data: Dictionary containing:
                - curated: {summary, rewritten_content, entities, hashtags}
                - platforms: {website, telegram, instagram}
                - processed_at: datetime
                
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            from bson import ObjectId
            
            update_data = {
                'status': 'processed',
                'updatedAt': datetime.utcnow(),
                **curated_data
            }
            
            result = self.collection.update_one(
                {'_id': ObjectId(article_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.debug(f"Updated article {article_id} with curated content")
                return True
            else:
                logger.warning(f"No article found with id {article_id}")
                return False
                
        except PyMongoError as e:
            logger.error(f"Failed to update article with curated content: {e}")
            return False
    
    def get_processed_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get articles with 'processed' status ready for publishing."""
        try:
            articles = list(self.collection.find({'status': 'processed'}).limit(limit))
            return articles
        except PyMongoError as e:
            logger.error(f"Failed to fetch processed articles: {e}")
            return []
