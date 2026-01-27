"""
Agent 5: Telegram Bot Agent
Manages Telegram subscriptions and broadcasts news to subscribers.

Features:
- /start - Subscribe to news updates
- /stop - Unsubscribe from updates  
- /status - Check subscription status
- Broadcasts news with images when new articles are processed
"""

import logging
import asyncio
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb import MongoDBManager

logger = logging.getLogger(__name__)


class TelegramBotAgent:
    """
    Telegram Bot Agent for subscriber management and news broadcasting.
    
    Features:
    - Subscriber management (add/remove via commands)
    - News broadcasting to all subscribers
    - Integration with existing pipeline
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the Telegram bot agent.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.db = self._init_database()
        
        # Telegram config
        telegram_config = self.config.get('TELEGRAM', {})
        self.bot_token = telegram_config.get('BOT_TOKEN', '')
        self.enabled = telegram_config.get('ENABLED', False)
        self.website_url = telegram_config.get('WEBSITE_URL', 'https://llm-news-nu.vercel.app')
        self.channel_id = telegram_config.get('CHANNEL_ID', '')  # Channel to post to
        
        if not self.bot_token or self.bot_token == 'your_bot_token_here':
            logger.warning("Telegram bot token not configured")
            self.enabled = False
        
        # Log channel mode if configured
        if self.channel_id:
            logger.info(f"Channel mode enabled: posting to {self.channel_id}")
        
        self.bot = None
        self.application = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def _init_database(self) -> MongoDBManager:
        """Initialize MongoDB connection."""
        mongo_config = self.config['MONGODB']
        db = MongoDBManager(
            connection_url=mongo_config['CONNECTION_URL'],
            database_name=mongo_config['DATABASE_NAME'],
            collection_name=mongo_config['COLLECTION_NAME']
        )
        if not db.connect():
            raise ConnectionError("Failed to connect to MongoDB")
        return db
    
    # ==================== Command Handlers ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Subscribe user to news updates."""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name or "Unknown"
        
        logger.info(f"New subscription request from {username} (chat_id: {chat_id})")
        
        # Add subscriber to database
        success = self.db.add_telegram_subscriber(chat_id, username)
        
        if success:
            welcome_message = (
                "🎉 *Welcome to LLM News!*\n\n"
                "You're now subscribed to receive the latest AI and tech news "
                "delivered straight to your Telegram.\n\n"
                "📰 You'll receive updates whenever new articles are published.\n\n"
                "Commands:\n"
                "• /stop - Unsubscribe from updates\n"
                "• /status - Check your subscription status"
            )
        else:
            # Already subscribed
            welcome_message = (
                "👋 *You're already subscribed!*\n\n"
                "You'll continue receiving news updates.\n\n"
                "Commands:\n"
                "• /stop - Unsubscribe from updates\n"
                "• /status - Check your subscription status"
            )
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command - Unsubscribe user from news updates."""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name or "Unknown"
        
        logger.info(f"Unsubscribe request from {username} (chat_id: {chat_id})")
        
        # Remove subscriber from database
        success = self.db.remove_telegram_subscriber(chat_id)
        
        if success:
            message = (
                "👋 *You've been unsubscribed*\n\n"
                "You won't receive any more news updates.\n\n"
                "Want to come back? Just send /start anytime!"
            )
        else:
            message = (
                "🤔 *You weren't subscribed*\n\n"
                "Want to subscribe? Send /start to get news updates!"
            )
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - Check subscription status."""
        chat_id = update.effective_chat.id
        
        is_subscribed = self.db.is_telegram_subscriber(chat_id)
        
        if is_subscribed:
            message = (
                "✅ *You're subscribed!*\n\n"
                "You'll receive news updates as they're published."
            )
        else:
            message = (
                "❌ *You're not subscribed*\n\n"
                "Send /start to subscribe and receive news updates!"
            )
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    # ==================== Broadcasting ====================
    
    async def broadcast_article(self, article: Dict) -> Dict[str, int]:
        """
        Broadcast a single article to channel (preferred) or subscribers.
        
        If CHANNEL_ID is configured, posts to the channel.
        Otherwise, falls back to individual subscriber broadcasting.
        
        Args:
            article: Article dictionary from database
            
        Returns:
            Dict with 'sent' and 'failed' counts
        """
        if not self.enabled:
            logger.warning("Telegram broadcasting is disabled")
            return {'sent': 0, 'failed': 0}
        
        article_id = str(article.get('_id', ''))
        
        # Get Telegram content
        platforms = article.get('platforms', {})
        telegram_content = platforms.get('telegram', {})
        teaser = telegram_content.get('teaser', '')
        
        if not teaser:
            logger.warning(f"No Telegram teaser for article {article_id}")
            return {'sent': 0, 'failed': 0}
        
        # Get image URL
        images = article.get('images', {})
        telegram_image = images.get('telegram', {})
        image_url = telegram_image.get('url', '')
        
        # Get website content for title
        website_content = platforms.get('website', {})
        title = website_content.get('title', article.get('title', 'News Update'))
        
        # Build article link
        article_link = f"{self.website_url}/article/{article_id}"
        
        # Format message
        message = f"📰 *{title}*\n\n{teaser}\n\n🔗 [Read more]({article_link})"
        
        # Initialize bot for sending
        bot = Bot(token=self.bot_token)
        
        sent = 0
        failed = 0
        
        # CHANNEL MODE: Post to channel if configured
        if self.channel_id:
            logger.info(f"Posting article to channel: {self.channel_id}")
            try:
                if image_url:
                    await bot.send_photo(
                        chat_id=self.channel_id,
                        photo=image_url,
                        caption=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await bot.send_message(
                        chat_id=self.channel_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=False
                    )
                sent = 1
                logger.info(f"Successfully posted to channel {self.channel_id}")
            except Exception as e:
                logger.error(f"Failed to post to channel {self.channel_id}: {e}")
                failed = 1
        
        # SUBSCRIBER MODE: Fallback to individual subscribers
        else:
            subscribers = self.db.get_all_telegram_subscribers()
            
            if not subscribers:
                logger.info("No subscribers to broadcast to")
                return {'sent': 0, 'failed': 0}
            
            logger.info(f"Broadcasting article to {len(subscribers)} subscribers")
            
            for subscriber in subscribers:
                chat_id = subscriber.get('chat_id')
                if not chat_id:
                    continue
                
                try:
                    if image_url:
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=image_url,
                            caption=message,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    else:
                        await bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=False
                        )
                    sent += 1
                    logger.debug(f"Sent to {chat_id}")
                    await asyncio.sleep(0.1)  # Rate limit delay
                except Exception as e:
                    logger.error(f"Failed to send to {chat_id}: {e}")
                    failed += 1
        
        # Mark article as broadcasted
        self.db.mark_article_broadcasted(article_id)
        
        logger.info(f"Broadcast complete: {sent} sent, {failed} failed")
        return {'sent': sent, 'failed': failed}
    
    def run(self) -> Dict[str, Any]:
        """
        Run the Telegram broadcast agent.
        
        Broadcasts all articles that haven't been sent to Telegram yet.
        
        Returns:
            Summary of broadcast operation
        """
        if not self.enabled:
            logger.info("Telegram bot is disabled in config")
            return {
                'articles_broadcast': 0,
                'total_sent': 0,
                'total_failed': 0,
                'enabled': False
            }
        
        start_time = datetime.utcnow()
        
        # Get articles to broadcast (processed but not yet broadcasted)
        articles = self.db.get_articles_to_broadcast(limit=10)
        
        if not articles:
            logger.info("No articles to broadcast")
            return {
                'articles_broadcast': 0,
                'total_sent': 0,
                'total_failed': 0,
                'enabled': True
            }
        
        logger.info(f"Found {len(articles)} articles to broadcast")
        
        total_sent = 0
        total_failed = 0
        articles_broadcast = 0
        
        # Run broadcasting in async context
        async def broadcast_all():
            nonlocal total_sent, total_failed, articles_broadcast
            
            for article in articles:
                result = await self.broadcast_article(article)
                total_sent += result['sent']
                total_failed += result['failed']
                if result['sent'] > 0:
                    articles_broadcast += 1
        
        # Run the async function
        asyncio.run(broadcast_all())
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        summary = {
            'articles_broadcast': articles_broadcast,
            'total_sent': total_sent,
            'total_failed': total_failed,
            'duration_seconds': round(duration, 2),
            'enabled': True
        }
        
        logger.info(f"Telegram broadcast complete: {articles_broadcast} articles, "
                   f"{total_sent} messages sent in {duration:.1f}s")
        
        return summary
    
    def start_bot(self):
        """
        Start the Telegram bot for handling commands.
        
        This runs the bot in polling mode to handle /start, /stop, /status commands.
        """
        if not self.enabled:
            logger.error("Cannot start bot - not configured or disabled")
            return
        
        logger.info("Starting Telegram bot...")
        
        # Create application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Run the bot
        logger.info("Bot is running. Press Ctrl+C to stop.")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    def close(self):
        """Clean up resources."""
        if self.db:
            self.db.disconnect()
            logger.info("Telegram bot agent closed")


# For running as a standalone script (bot mode)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Telegram Bot Agent")
    parser.add_argument("--broadcast", action="store_true", 
                       help="Broadcast pending articles and exit")
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  TELEGRAM BOT AGENT")
    print("="*60 + "\n")
    
    try:
        agent = TelegramBotAgent()
        
        if args.broadcast:
            # Broadcast mode - send pending articles
            print("Broadcasting pending articles...")
            result = agent.run()
            print(f"\nResults:")
            print(f"  Articles broadcast: {result['articles_broadcast']}")
            print(f"  Messages sent: {result['total_sent']}")
            print(f"  Failed: {result['total_failed']}")
        else:
            # Bot mode - run continuously for commands
            print("Starting bot in command mode...")
            print("Users can now interact with /start, /stop, /status")
            agent.start_bot()
            
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'agent' in locals():
            agent.close()
