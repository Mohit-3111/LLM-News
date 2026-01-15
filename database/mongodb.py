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
                'status': 'curated',  # curated -> generating_images -> processed
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
    
    def get_articles_for_image_generation(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get articles that are curated but don't have images yet.
        
        Returns articles with status 'curated'.
        """
        try:
            query = {'status': 'curated'}
            articles = list(self.collection.find(query).limit(limit))
            return articles
        except PyMongoError as e:
            logger.error(f"Failed to fetch articles for image generation: {e}")
            return []
    
    def mark_article_generating_images(self, article_id: str) -> bool:
        """Mark an article as currently generating images."""
        try:
            from bson import ObjectId
            result = self.collection.update_one(
                {'_id': ObjectId(article_id)},
                {'$set': {'status': 'generating_images', 'updatedAt': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Failed to mark article as generating: {e}")
            return False
    
    def update_article_images(self, article_id: str, image_data: Dict[str, Any]) -> bool:
        """
        Update an article with generated image data.
        
        Args:
            article_id: MongoDB ObjectId string
            image_data: Dictionary containing:
                - images: {website, telegram, instagram} with paths and metadata
                - image_prompts: List of prompts used
                - images_generated_at: datetime
                
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            from bson import ObjectId
            
            update_data = {
                'status': 'processed',  # Final status - ready for publishing
                'updatedAt': datetime.utcnow(),
                **image_data
            }
            
            result = self.collection.update_one(
                {'_id': ObjectId(article_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.debug(f"Updated article {article_id} with image data")
                return True
            else:
                logger.warning(f"No article found with id {article_id}")
                return False
                
        except PyMongoError as e:
            logger.error(f"Failed to update article with images: {e}")
            return False
    
    def get_processed_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get articles with 'processed' status ready for publishing."""
        try:
            articles = list(self.collection.find({'status': 'processed'}).limit(limit))
            return articles
        except PyMongoError as e:
            logger.error(f"Failed to fetch processed articles: {e}")
            return []
    
    def get_articles_with_incomplete_images(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get articles that have incomplete image sets (some images failed to generate)
        AND have not exceeded the maximum retry count (3 retries per platform).
        """
        try:
            MAX_RETRIES = 3
            # Find articles where:
            # 1. Status is 'processed' but some images are missing
            # 2. Retry count is less than MAX_RETRIES
            query = {
                'status': 'processed',
                'images': {'$exists': True},
                '$or': [
                    {'images.website': None},
                    {'images.telegram': None},
                    {'images.instagram': {'$size': 0}},
                    {'images.instagram': {'$elemMatch': {'url': None}}}  # Fixed: was 'path'
                ],
                # Only retry if under max retry count
                '$or': [
                    {'image_retry_count': {'$exists': False}},
                    {'image_retry_count': {'$lt': MAX_RETRIES}}
                ]
            }
            articles = list(self.collection.find(query).limit(limit))
            return articles
        except PyMongoError as e:
            logger.error(f"Failed to fetch articles with incomplete images: {e}")
            return []
    
    def mark_article_for_image_retry(self, article_id: str) -> bool:
        """Mark an article to be retried for image generation and increment retry count."""
        try:
            from bson import ObjectId
            result = self.collection.update_one(
                {'_id': ObjectId(article_id)},
                {
                    '$set': {
                        'status': 'curated',  # Reset to curated for image retry
                        'updatedAt': datetime.utcnow()
                    },
                    '$inc': {'image_retry_count': 1},  # Increment retry count
                    '$unset': {'images': '', 'image_prompts': ''}  # Clear old image data
                }
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Failed to mark article for image retry: {e}")
            return False
    
    def get_article_retry_count(self, article_id: str) -> int:
        """Get the current retry count for an article."""
        try:
            from bson import ObjectId
            article = self.collection.find_one(
                {'_id': ObjectId(article_id)},
                {'image_retry_count': 1}
            )
            return article.get('image_retry_count', 0) if article else 0
        except PyMongoError as e:
            logger.error(f"Failed to get retry count: {e}")
            return 0
    
    # ==================== Telegram Subscriber Methods ====================
    
    def _get_subscribers_collection(self):
        """Get the telegram_subscribers collection."""
        return self.db['telegram_subscribers']
    
    def add_telegram_subscriber(self, chat_id: int, username: str) -> bool:
        """
        Add a new Telegram subscriber.
        
        Args:
            chat_id: Telegram chat ID
            username: Telegram username or display name
            
        Returns:
            True if added, False if already exists
        """
        try:
            subscribers = self._get_subscribers_collection()
            
            # Check if already subscribed
            existing = subscribers.find_one({'chat_id': chat_id})
            if existing:
                logger.debug(f"Subscriber {chat_id} already exists")
                return False
            
            # Add new subscriber
            subscribers.insert_one({
                'chat_id': chat_id,
                'username': username,
                'subscribed_at': datetime.utcnow(),
                'active': True
            })
            
            logger.info(f"Added Telegram subscriber: {username} ({chat_id})")
            return True
            
        except PyMongoError as e:
            logger.error(f"Failed to add subscriber: {e}")
            return False
    
    def remove_telegram_subscriber(self, chat_id: int) -> bool:
        """
        Remove a Telegram subscriber.
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            True if removed, False if not found
        """
        try:
            subscribers = self._get_subscribers_collection()
            result = subscribers.delete_one({'chat_id': chat_id})
            
            if result.deleted_count > 0:
                logger.info(f"Removed Telegram subscriber: {chat_id}")
                return True
            return False
            
        except PyMongoError as e:
            logger.error(f"Failed to remove subscriber: {e}")
            return False
    
    def is_telegram_subscriber(self, chat_id: int) -> bool:
        """Check if a chat_id is subscribed."""
        try:
            subscribers = self._get_subscribers_collection()
            existing = subscribers.find_one({'chat_id': chat_id, 'active': True})
            return existing is not None
        except PyMongoError as e:
            logger.error(f"Failed to check subscriber: {e}")
            return False
    
    def get_all_telegram_subscribers(self) -> List[Dict[str, Any]]:
        """Get all active Telegram subscribers."""
        try:
            subscribers = self._get_subscribers_collection()
            return list(subscribers.find({'active': True}))
        except PyMongoError as e:
            logger.error(f"Failed to fetch subscribers: {e}")
            return []
    
    def get_telegram_subscriber_count(self) -> int:
        """Get count of active subscribers."""
        try:
            subscribers = self._get_subscribers_collection()
            return subscribers.count_documents({'active': True})
        except PyMongoError as e:
            logger.error(f"Failed to count subscribers: {e}")
            return 0
    
    # ==================== Telegram Broadcast Methods ====================
    
    def get_articles_to_broadcast(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get processed articles that haven't been broadcast to Telegram yet.
        
        Returns articles with status 'processed' and no telegram_broadcast field.
        """
        try:
            query = {
                'status': 'processed',
                'telegram_broadcast': {'$ne': True}
            }
            articles = list(self.collection.find(query).sort('processed_at', -1).limit(limit))
            return articles
        except PyMongoError as e:
            logger.error(f"Failed to fetch articles for broadcast: {e}")
            return []
    
    def mark_article_broadcasted(self, article_id: str) -> bool:
        """
        Mark an article as broadcast to Telegram.
        
        Args:
            article_id: MongoDB ObjectId string
            
        Returns:
            True if marked successfully
        """
        try:
            from bson import ObjectId
            result = self.collection.update_one(
                {'_id': ObjectId(article_id)},
                {'$set': {
                    'telegram_broadcast': True,
                    'telegram_broadcast_at': datetime.utcnow()
                }}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Failed to mark article as broadcasted: {e}")
            return False


