"""
Agent 3: Content Curation & LLM Agent
Processes raw articles using Groq LLM to generate platform-specific content.
"""

import logging
import time
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime

from groq import Groq

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb import MongoDBManager

logger = logging.getLogger(__name__)


class ContentCurationAgent:
    """
    Content Curation Agent that processes raw articles through LLM.
    
    Pipeline:
    1. Fetch raw articles from MongoDB
    2. Summarize and rewrite content
    3. Extract key entities (people, organizations, locations)
    4. Generate hashtags
    5. Create platform-specific content (Website, Telegram, Instagram)
    6. Update database with processed content
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the content curation agent.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.groq_client = self._init_llm()
        self.db = self._init_database()
        
        # Settings
        self.batch_size = self.config.get('CONTENT_CURATION', {}).get('BATCH_SIZE', 10)
        self.delay_between_calls = self.config.get('CONTENT_CURATION', {}).get('DELAY_BETWEEN_CALLS', 2)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def _init_llm(self) -> Groq:
        """Initialize Groq LLM client."""
        llm_config = self.config.get('LLM', {})
        api_key = llm_config.get('API_KEY')
        
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("Please set your Groq API key in config.yaml")
        
        client = Groq(api_key=api_key)
        logger.info("Groq LLM client initialized")
        return client
    
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
    
    def _call_llm(self, prompt: str, system_prompt: str = None, max_tokens: int = None) -> str:
        """
        Make a call to the Groq LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Max tokens for response (default from config)
            
        Returns:
            LLM response text
        """
        llm_config = self.config.get('LLM', {})
        model = llm_config.get('MODEL', 'llama-3.3-70b-versatile')
        temperature = llm_config.get('TEMPERATURE', 0.7)
        max_tokens = max_tokens or llm_config.get('MAX_TOKENS', 2048)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Rate limiting delay
            time.sleep(self.delay_between_calls)
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _summarize_and_rewrite(self, article: Dict) -> Dict:
        """
        Summarize and rewrite the article to avoid plagiarism.
        
        Returns:
            Dict with 'summary' and 'rewritten_content'
        """
        title = article.get('title', '')
        content = article.get('full_content') or article.get('content', '')
        
        if not content:
            logger.warning(f"No content for article: {title}")
            return {'summary': '', 'rewritten_content': ''}
        
        # Truncate content if too long (to stay within token limits)
        content = content[:7000]
        
        system_prompt = """You are a professional news editor. Your task is to:
1. Summarize the article in 2-3 sentences
2. Rewrite the main content in a fresh, original way to avoid plagiarism

Maintain factual accuracy while creating unique content."""

        prompt = f"""Article Title: {title}

Article Content:
{content}

Please provide:
1. SUMMARY: A 2-3 sentence summary of the key points
2. REWRITTEN: A rewritten version of the article (3 paragraphs, keeping all important facts)

Format your response exactly as:
SUMMARY:
[your summary here]

REWRITTEN:
[your rewritten content here]"""

        response = self._call_llm(prompt, system_prompt)
        
        # Parse response
        summary = ""
        rewritten = ""
        
        if "SUMMARY:" in response and "REWRITTEN:" in response:
            parts = response.split("REWRITTEN:")
            summary = parts[0].replace("SUMMARY:", "").strip()
            rewritten = parts[1].strip() if len(parts) > 1 else ""
        else:
            # Fallback - use whole response as summary
            summary = response[:500]
            rewritten = response
        
        return {
            'summary': summary,
            'rewritten_content': rewritten
        }
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract key entities from text.
        
        Returns:
            Dict with 'people', 'organizations', 'locations'
        """
        if not text:
            return {'people': [], 'organizations': [], 'locations': []}
        
        system_prompt = "You are an entity extraction expert. Extract named entities from news articles."
        
        prompt = f"""Extract the following entities from this text:

Text: {text[:2000]}

Provide your response in this exact format:
PEOPLE: [comma-separated list of person names, or "none" if none found]
ORGANIZATIONS: [comma-separated list of organization names, or "none" if none found]
LOCATIONS: [comma-separated list of location names, or "none" if none found]"""

        response = self._call_llm(prompt, system_prompt, max_tokens=500)
        
        entities = {'people': [], 'organizations': [], 'locations': []}
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('PEOPLE:'):
                items = line.replace('PEOPLE:', '').strip()
                if items.lower() != 'none':
                    entities['people'] = [x.strip() for x in items.split(',') if x.strip()]
            elif line.startswith('ORGANIZATIONS:'):
                items = line.replace('ORGANIZATIONS:', '').strip()
                if items.lower() != 'none':
                    entities['organizations'] = [x.strip() for x in items.split(',') if x.strip()]
            elif line.startswith('LOCATIONS:'):
                items = line.replace('LOCATIONS:', '').strip()
                if items.lower() != 'none':
                    entities['locations'] = [x.strip() for x in items.split(',') if x.strip()]
        
        return entities
    
    def _generate_hashtags(self, text: str, entities: Dict) -> List[str]:
        """Generate relevant hashtags for social media."""
        if not text:
            return []
        
        entity_hints = []
        for category, items in entities.items():
            entity_hints.extend(items[:3])
        
        system_prompt = "You are a social media expert. Generate relevant, trending hashtags for news content."
        
        prompt = f"""Generate 5-8 relevant hashtags for this news article.

Article summary: {text[:500]}
Key entities: {', '.join(entity_hints) if entity_hints else 'N/A'}

Rules:
- Start each hashtag with #
- Use CamelCase for multi-word hashtags
- Include a mix of specific and broad hashtags
- Make them social media friendly

Provide hashtags as a comma-separated list:"""

        response = self._call_llm(prompt, system_prompt, max_tokens=200)
        
        # Parse hashtags
        hashtags = []
        for tag in response.replace('\n', ',').split(','):
            tag = tag.strip()
            if tag.startswith('#'):
                hashtags.append(tag)
            elif tag:
                hashtags.append(f"#{tag}")
        
        return hashtags[:8]  # Limit to 8 hashtags
    
    def _generate_website_content(self, article: Dict, summary: str, rewritten: str) -> Dict:
        """
        Generate professional website content.
        
        Returns:
            Dict with 'title', 'summary', 'paragraphs'
        """
        original_title = article.get('title', '')
        
        system_prompt = """You are a professional news writer for a technology news website.
Your writing style is:
- Professional and detailed
- Clear and informative
- Engaging but factual"""

        prompt = f"""Create website content for this news article.

Original Title: {original_title}
Summary: {summary}
Content: {rewritten[:2000]}

Generate:
1. An engaging, SEO-friendly headline (different from original)
2. A professional summary paragraph (2-3 sentences)
3. Three detailed content paragraphs

Format your response exactly as:
HEADLINE:
[your headline]

SUMMARY:
[your summary paragraph]

PARAGRAPH_1:
[first paragraph]

PARAGRAPH_2:
[second paragraph]

PARAGRAPH_3:
[third paragraph]"""

        response = self._call_llm(prompt, system_prompt)
        
        # Parse response
        result = {
            'title': original_title,
            'summary': summary,
            'paragraphs': []
        }
        
        sections = {
            'HEADLINE:': 'title',
            'SUMMARY:': 'summary'
        }
        
        current_section = None
        lines = response.split('\n')
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            if line_stripped in ['HEADLINE:', 'SUMMARY:']:
                current_section = sections.get(line_stripped)
            elif line_stripped.startswith('PARAGRAPH_'):
                # Collect remaining lines until next section
                para_lines = []
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith('PARAGRAPH_') or lines[j].strip() in sections:
                        break
                    if lines[j].strip():
                        para_lines.append(lines[j].strip())
                if para_lines:
                    result['paragraphs'].append(' '.join(para_lines))
            elif current_section and line_stripped:
                result[current_section] = line_stripped
                current_section = None
        
        # Ensure we have 3 paragraphs
        while len(result['paragraphs']) < 3:
            result['paragraphs'].append(rewritten[:500] if rewritten else summary)
        
        return result
    
    def _generate_telegram_content(self, article: Dict, summary: str) -> Dict:
        """
        Generate conversational Telegram teaser.
        
        Returns:
            Dict with 'teaser'
        """
        title = article.get('title', '')
        
        system_prompt = """You are a social media manager creating Telegram post teasers.
Your style is:
- Conversational and catchy
- Uses emojis sparingly but effectively
- Creates curiosity to click the link
- Friendly and engaging"""

        prompt = f"""Create a Telegram teaser for this news article.

Title: {title}
Summary: {summary}

Write a catchy 2-3 sentence teaser that:
- Starts with a relevant emoji
- Hooks the reader immediately
- Creates curiosity to read more
- Sounds conversational, not robotic

Just provide the teaser text, nothing else:"""

        teaser = self._call_llm(prompt, system_prompt, max_tokens=300)
        
        return {'teaser': teaser.strip()}
    
    def _generate_instagram_content(self, article: Dict, summary: str, hashtags: List[str]) -> Dict:
        """
        Generate Instagram caption with hashtags.
        
        Returns:
            Dict with 'caption', 'hashtags'
        """
        title = article.get('title', '')
        
        system_prompt = """You are an Instagram content creator for a tech news account.
Your style is:
- Very catchy and attention-grabbing
- Uses emojis effectively
- Short and punchy
- Encourages engagement"""

        prompt = f"""Create an Instagram caption for this news.

Title: {title}
Summary: {summary}

Write a catchy 1-2 sentence caption that:
- Starts with an attention-grabbing emoji
- Is punchy and memorable
- Encourages engagement (like, comment, share)
- Fits Instagram's casual vibe

Just provide the caption text, no hashtags:"""

        caption = self._call_llm(prompt, system_prompt, max_tokens=200)
        
        return {
            'caption': caption.strip(),
            'hashtags': hashtags
        }
    
    def process_article(self, article: Dict) -> Optional[Dict]:
        """
        Process a single article through the full curation pipeline.
        
        Args:
            article: Raw article from database
            
        Returns:
            Curated content dictionary or None if failed
        """
        article_id = str(article.get('_id', ''))
        title = article.get('title', 'Unknown')[:50]
        
        logger.info(f"Processing article: {title}...")
        
        try:
            # Step 1: Summarize and rewrite
            logger.debug("Step 1: Summarizing and rewriting...")
            summary_result = self._summarize_and_rewrite(article)
            summary = summary_result['summary']
            rewritten = summary_result['rewritten_content']
            
            # Step 2: Extract entities
            logger.debug("Step 2: Extracting entities...")
            content_for_entities = rewritten or article.get('full_content', '') or article.get('content', '')
            entities = self._extract_entities(content_for_entities)
            
            # Step 3: Generate hashtags
            logger.debug("Step 3: Generating hashtags...")
            hashtags = self._generate_hashtags(summary, entities)
            
            # Step 4: Generate platform-specific content
            logger.debug("Step 4: Generating platform content...")
            website_content = self._generate_website_content(article, summary, rewritten)
            telegram_content = self._generate_telegram_content(article, summary)
            instagram_content = self._generate_instagram_content(article, summary, hashtags)
            
            # Compile results
            curated_data = {
                'curated': {
                    'summary': summary,
                    'rewritten_content': rewritten,
                    'entities': entities,
                    'hashtags': hashtags
                },
                'platforms': {
                    'website': website_content,
                    'telegram': telegram_content,
                    'instagram': instagram_content
                },
                'processed_at': datetime.utcnow()
            }
            
            # Update database
            success = self.db.update_article_curated_content(article_id, curated_data)
            if success:
                logger.info(f"Successfully processed: {title}")
            else:
                logger.warning(f"Failed to update database for: {title}")
            
            return curated_data
            
        except Exception as e:
            logger.error(f"Failed to process article {title}: {e}")
            return None
    
    def run(self, batch_size: int = None) -> Dict[str, Any]:
        """
        Run the content curation agent on raw articles.
        
        Args:
            batch_size: Number of articles to process (default from config)
            
        Returns:
            Summary of processing results
        """
        batch_size = batch_size or self.batch_size
        start_time = datetime.utcnow()
        
        logger.info(f"Starting content curation (batch size: {batch_size})")
        
        # Fetch raw articles
        raw_articles = self.db.get_raw_articles(limit=batch_size)
        
        if not raw_articles:
            logger.info("No raw articles to process")
            return {
                'processed': 0,
                'failed': 0,
                'total_raw': 0,
                'duration_seconds': 0
            }
        
        logger.info(f"Found {len(raw_articles)} raw articles to process")
        
        processed = 0
        failed = 0
        
        for i, article in enumerate(raw_articles, 1):
            logger.info(f"[{i}/{len(raw_articles)}] Processing article...")
            
            result = self.process_article(article)
            if result:
                processed += 1
            else:
                failed += 1
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        summary = {
            'processed': processed,
            'failed': failed,
            'total_raw': len(raw_articles),
            'duration_seconds': round(duration, 2)
        }
        
        logger.info(f"Content curation complete: {processed} processed, {failed} failed in {duration:.1f}s")
        
        return summary
    
    def close(self):
        """Clean up resources."""
        if self.db:
            self.db.disconnect()
            logger.info("Content curation agent closed")


# For running as a standalone script
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("\n" + "="*60)
    print("  CONTENT CURATION AGENT - Standalone Test")
    print("="*60 + "\n")
    
    try:
        agent = ContentCurationAgent()
        
        # Run curation
        results = agent.run(batch_size=2)  # Process just 2 for testing
        
        print("\n" + "-"*40)
        print("Results:")
        print(f"  Processed: {results['processed']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Duration: {results['duration_seconds']}s")
        print("-"*40)
        
        # Show database stats
        stats = agent.db.get_article_count()
        print("\nDatabase Statistics:")
        for status, count in stats.items():
            print(f"  {status}: {count}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'agent' in locals():
            agent.close()
