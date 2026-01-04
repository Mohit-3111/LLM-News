"""
Agent 4: Image Creation Agent
Generates AI images for articles using Pollinations.ai (free, unlimited API).

Pipeline:
1. Fetch processed articles from MongoDB
2. Generate creative image prompts using LLM
3. Create images via Pollinations.ai API
4. Save images locally (AWS S3 integration later)
5. Update database with image paths
"""

import logging
import time
import yaml
import os
import hashlib
import urllib.parse
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from groq import Groq

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb import MongoDBManager

logger = logging.getLogger(__name__)


class ImageCreationAgent:
    """
    Image Creation Agent that generates AI images for articles.
    
    Uses Pollinations.ai - a free, unlimited image generation API.
    
    Image Distribution:
    - Website: 1 image (landscape 16:9)
    - Telegram: 1 image (square)
    - Instagram: 3 images (portrait, carousel post)
    """
    
    # Pollinations.ai API base URL
    POLLINATIONS_API = "https://image.pollinations.ai/prompt"
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the image creation agent.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.groq_client = self._init_llm()
        self.db = self._init_database()
        
        # Image generation settings
        img_config = self.config.get('IMAGE_GENERATION', {})
        self.enabled = img_config.get('ENABLED', True)
        self.output_dir = img_config.get('OUTPUT_DIR', 'generated_images')
        self.batch_size = img_config.get('BATCH_SIZE', 10)
        self.delay_between_calls = img_config.get('DELAY_BETWEEN_CALLS', 1)
        
        # Platform-specific dimensions
        self.dimensions = {
            'website': {
                'width': img_config.get('WEBSITE', {}).get('WIDTH', 1280),
                'height': img_config.get('WEBSITE', {}).get('HEIGHT', 720)
            },
            'telegram': {
                'width': img_config.get('TELEGRAM', {}).get('WIDTH', 512),
                'height': img_config.get('TELEGRAM', {}).get('HEIGHT', 512)
            },
            'instagram': {
                'width': img_config.get('INSTAGRAM', {}).get('WIDTH', 1080),
                'height': img_config.get('INSTAGRAM', {}).get('HEIGHT', 1350)
            }
        }
        
        # Create output directory
        self._ensure_output_dir()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def _init_llm(self) -> Groq:
        """Initialize Groq LLM client for prompt generation."""
        llm_config = self.config.get('LLM', {})
        api_key = llm_config.get('API_KEY')
        
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("Please set your Groq API key in config.yaml")
        
        client = Groq(api_key=api_key)
        logger.info("Groq LLM client initialized for image prompt generation")
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
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Image output directory: {self.output_dir}")
    
    def _call_llm(self, prompt: str, system_prompt: str = None, max_tokens: int = 500) -> str:
        """
        Make a call to the Groq LLM with rate limit handling.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Max tokens for response
            
        Returns:
            LLM response text
        """
        llm_config = self.config.get('LLM', {})
        model = llm_config.get('MODEL', 'llama-3.3-70b-versatile')
        temperature = llm_config.get('TEMPERATURE', 0.7)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.groq_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Add delay after successful call to avoid rate limits
                time.sleep(2)
                
                return response.choices[0].message.content.strip()
            except Exception as e:
                error_str = str(e).lower()
                if 'rate_limit' in error_str or 'rate limit' in error_str:
                    wait_time = (2 ** attempt) * 10  # 10, 20, 40 seconds
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"LLM call failed: {e}")
                    raise
        
        logger.error("All LLM retry attempts exhausted due to rate limits")
        raise Exception("Rate limit exceeded after all retries")
    
    def _generate_image_prompts(self, article: Dict) -> List[str]:
        """
        Generate 3 creative image prompts based on article content.
        
        Args:
            article: Article dictionary with curated content
            
        Returns:
            List of 3 image generation prompts
        """
        # Extract article information
        title = article.get('title', '')
        curated = article.get('curated', {})
        summary = curated.get('summary', '')
        entities = curated.get('entities', {})
        
        # Build context for LLM
        people = ', '.join(entities.get('people', [])[:3]) or 'None mentioned'
        orgs = ', '.join(entities.get('organizations', [])[:3]) or 'N/A'
        locations = ', '.join(entities.get('locations', [])[:3]) or 'N/A'
        
        # Check if story is about specific people
        has_people = people != 'None mentioned'
        
        system_prompt = """You are an expert at creating image prompts for realistic AI-generated photographs.
Your goal is to create prompts that result in HIGH QUALITY, REALISTIC news photography.

TIPS FOR BEST RESULTS:
1. Use medium shots or wide shots of people (not extreme close-ups)
2. Show people in natural poses and environments
3. Focus on action, movement, or candid moments
4. Include environment context (office, stadium, street, etc.)
5. Describe lighting: natural light, golden hour, studio lighting

PROMPT STRUCTURE:
- Describe the scene naturally like a photograph
- Include: subject, action/pose, environment, lighting, mood
- Add quality keywords at the end
- Keep prompts focused and clear (max 60 words)

EXAMPLE GOOD PROMPTS:
- "Business professional giving presentation in modern conference room, audience visible, natural daylight from windows, professional photography"
- "Athlete celebrating victory on sports field, dramatic stadium lighting, action shot, photojournalism style"
- "Scientists working together in high-tech laboratory, equipment visible, soft lighting, editorial photography"
"""

        prompt = f"""Create 3 realistic news photography prompts for this article.

Article Title: {title}
Summary: {summary}
Key People: {people}
Organizations: {orgs}
Locations: {locations}

Create 3 different photograph descriptions:
1. Main hero image - the primary visual for the story{' (show relevant people in context)' if has_people else ''}
2. Secondary angle or related scene
3. Detail or environmental shot

Make images look like real news photography - natural, candid, professional.

Format:
PROMPT_1: [realistic photo description]
PROMPT_2: [realistic photo description]  
PROMPT_3: [realistic photo description]"""

        response = self._call_llm(prompt, system_prompt)
        
        # Parse prompts from response
        prompts = []
        
        # Quality suffix optimized for turbo model
        quality_suffix = ", professional photography, realistic, high quality, sharp focus, natural lighting, photojournalism style"
        
        for line in response.split('\n'):
            line = line.strip()
            for prefix in ['PROMPT_1:', 'PROMPT_2:', 'PROMPT_3:']:
                if line.startswith(prefix):
                    prompt_text = line.replace(prefix, '').strip()
                    if prompt_text:
                        # Add quality keywords
                        prompt_text = prompt_text + quality_suffix
                        prompts.append(prompt_text)
                    break

        
        # Ensure we have 3 prompts
        while len(prompts) < 3:
            # Fallback: create object/environment focused prompts
            fallback = f"Modern technology and digital devices representing {title[:40]}, sleek design, professional product photography, 8k, dramatic lighting{quality_suffix}"
            prompts.append(fallback)
        
        return prompts[:3]
    
    def _generate_article_id_hash(self, article_id: str) -> str:
        """Generate a short hash for article ID to use in filenames."""
        return hashlib.md5(article_id.encode()).hexdigest()[:8]
    
    def _download_image(self, prompt: str, width: int, height: int, 
                        output_path: str, seed: int = None, max_retries: int = 3) -> bool:
        """
        Download an image from Pollinations.ai API with retry logic.
        
        Args:
            prompt: Image generation prompt
            width: Image width in pixels
            height: Image height in pixels
            output_path: Path to save the image
            seed: Optional seed for reproducibility
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        # Models to try in order of preference - turbo is more stable, flux for quality
        models_to_try = ['turbo', 'flux', 'seedream']
        
        for model in models_to_try:
            for attempt in range(max_retries):
                try:
                    # Encode prompt for URL
                    encoded_prompt = urllib.parse.quote(prompt)
                    
                    # Build URL with parameters
                    url = f"{self.POLLINATIONS_API}/{encoded_prompt}"
                    params = {
                        'width': width,
                        'height': height,
                        'nologo': 'true',
                        'model': model
                    }
                    if seed is not None:
                        params['seed'] = seed + attempt  # Vary seed on retry
                    
                    # Make request with longer timeout
                    logger.debug(f"Requesting image (model={model}, attempt={attempt+1}): {prompt[:50]}...")
                    response = requests.get(url, params=params, timeout=180)
                    
                    if response.status_code == 200:
                        # Verify we got actual image data
                        if len(response.content) > 1000:  # Valid images are larger
                            with open(output_path, 'wb') as f:
                                f.write(response.content)
                            logger.info(f"Saved image (model={model}): {output_path}")
                            return True
                        else:
                            logger.warning(f"Response too small, retrying...")
                    elif response.status_code in [502, 503, 504]:
                        # Server errors - retry with exponential backoff
                        wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                        logger.warning(f"HTTP {response.status_code}, retrying in {wait_time}s (attempt {attempt+1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Failed to generate image: HTTP {response.status_code}")
                        break  # Don't retry on other errors, try next model
                        
                except requests.exceptions.Timeout:
                    wait_time = (2 ** attempt) * 2
                    logger.warning(f"Timeout, retrying in {wait_time}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                except Exception as e:
                    logger.error(f"Error downloading image: {e}")
                    break
            
            # If we get here, all retries failed for this model, try next
            logger.warning(f"Model {model} failed, trying next model...")
        
        logger.error(f"All models and retries exhausted for image generation")
        return False
    
    def _generate_images_for_article(self, article: Dict, prompts: List[str]) -> Dict[str, Any]:
        """
        Generate all images for an article.
        
        Optimized to generate only 3 unique images:
        - Image 1: Website + Instagram (different dimensions)
        - Image 2: Telegram (reused for Instagram)
        - Image 3: Instagram only
        
        Args:
            article: Article dictionary
            prompts: List of 3 image prompts
            
        Returns:
            Dictionary with image metadata for each platform
        """
        article_id = str(article.get('_id', ''))
        article_hash = self._generate_article_id_hash(article_id)
        
        # Create article-specific directory
        article_dir = os.path.join(self.output_dir, article_hash)
        Path(article_dir).mkdir(parents=True, exist_ok=True)
        
        images = {
            'website': None,
            'telegram': None,
            'instagram': []
        }
        
        # Generate timestamp-based seed for reproducibility
        base_seed = int(datetime.utcnow().timestamp())
        
        # Generate Image 1: Website (landscape) - will also be used for Instagram
        logger.info("Generating image 1 (website)...")
        img1_path_web = os.path.join(article_dir, "website_01.jpg")
        
        success = self._download_image(
            prompt=prompts[0],
            width=self.dimensions['website']['width'],
            height=self.dimensions['website']['height'],
            output_path=img1_path_web,
            seed=base_seed
        )
        if success:
            images['website'] = {
                'path': img1_path_web,
                'prompt': prompts[0],
                'dimensions': self.dimensions['website']
            }
            # Also add to Instagram (cropped version conceptually)
            images['instagram'].append({
                'path': img1_path_web,
                'prompt': prompts[0],
                'dimensions': self.dimensions['website']
            })
        
        time.sleep(self.delay_between_calls)
        
        # Generate Image 2: Telegram (square) - also for Instagram
        logger.info("Generating image 2 (telegram)...")
        img2_path_tg = os.path.join(article_dir, "telegram_01.jpg")
        
        success = self._download_image(
            prompt=prompts[1],
            width=self.dimensions['telegram']['width'],
            height=self.dimensions['telegram']['height'],
            output_path=img2_path_tg,
            seed=base_seed + 1
        )
        if success:
            images['telegram'] = {
                'path': img2_path_tg,
                'prompt': prompts[1],
                'dimensions': self.dimensions['telegram']
            }
            images['instagram'].append({
                'path': img2_path_tg,
                'prompt': prompts[1],
                'dimensions': self.dimensions['telegram']
            })
        
        time.sleep(self.delay_between_calls)
        
        # Generate Image 3: Instagram portrait
        logger.info("Generating image 3 (instagram)...")
        img3_path_ig = os.path.join(article_dir, "instagram_01.jpg")
        
        success = self._download_image(
            prompt=prompts[2],
            width=self.dimensions['instagram']['width'],
            height=self.dimensions['instagram']['height'],
            output_path=img3_path_ig,
            seed=base_seed + 2
        )
        if success:
            images['instagram'].append({
                'path': img3_path_ig,
                'prompt': prompts[2],
                'dimensions': self.dimensions['instagram']
            })
        
        return images
    
    def process_article(self, article: Dict) -> Optional[Dict]:
        """
        Process a single article to generate images.
        
        Args:
            article: Article from database (with curated content)
            
        Returns:
            Image metadata dictionary or None if failed
        """
        article_id = str(article.get('_id', ''))
        title = article.get('title', 'Unknown')[:50]
        
        logger.info(f"Processing images for: {title}...")
        
        try:
            # Mark article as generating images
            self.db.mark_article_generating_images(article_id)
            
            # Step 1: Generate image prompts using LLM
            logger.debug("Generating image prompts...")
            prompts = self._generate_image_prompts(article)
            logger.info(f"Generated {len(prompts)} image prompts")
            
            # Rate limit delay after LLM call
            time.sleep(self.delay_between_calls)
            
            # Step 2: Generate images
            logger.debug("Generating images...")
            images = self._generate_images_for_article(article, prompts)
            
            # Count successful generations
            success_count = 0
            if images['website']:
                success_count += 1
            if images['telegram']:
                success_count += 1
            success_count += len(images['instagram'])
            
            logger.info(f"Generated {success_count} images for article")
            
            # Step 3: Update database
            image_data = {
                'images': images,
                'image_prompts': prompts,
                'images_generated_at': datetime.utcnow()
            }
            
            success = self.db.update_article_images(article_id, image_data)
            if success:
                logger.info(f"Successfully updated article with images: {title}")
            else:
                logger.warning(f"Failed to update database for: {title}")
            
            return images
            
        except Exception as e:
            logger.error(f"Failed to generate images for {title}: {e}")
            return None
    
    def run(self, batch_size: int = None) -> Dict[str, Any]:
        """
        Run the image creation agent on processed articles.
        
        Args:
            batch_size: Number of articles to process (default from config)
            
        Returns:
            Summary of processing results
        """
        if not self.enabled:
            logger.info("Image generation is disabled in config")
            return {'processed': 0, 'failed': 0, 'disabled': True}
        
        batch_size = batch_size or self.batch_size
        start_time = datetime.utcnow()
        
        logger.info(f"Starting image generation (batch size: {batch_size})")
        
        # Fetch articles ready for image generation
        articles = self.db.get_articles_for_image_generation(limit=batch_size)
        
        if not articles:
            logger.info("No articles ready for image generation")
            return {
                'processed': 0,
                'failed': 0,
                'total': 0,
                'duration_seconds': 0
            }
        
        logger.info(f"Found {len(articles)} articles for image generation")
        
        processed = 0
        failed = 0
        
        for i, article in enumerate(articles, 1):
            logger.info(f"[{i}/{len(articles)}] Generating images...")
            
            result = self.process_article(article)
            if result:
                processed += 1
            else:
                failed += 1
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        summary = {
            'processed': processed,
            'failed': failed,
            'total': len(articles),
            'duration_seconds': round(duration, 2)
        }
        
        logger.info(f"Image generation complete: {processed} processed, {failed} failed in {duration:.1f}s")
        
        # Retry incomplete image sets from previous runs
        if failed > 0 or processed > 0:
            retry_count = self.retry_failed_images()
            if retry_count > 0:
                summary['retried'] = retry_count
        
        return summary
    
    def retry_failed_images(self) -> int:
        """
        Retry image generation for articles that have incomplete image sets.
        This is called automatically at the end of each run cycle.
        
        Returns:
            Number of articles successfully retried
        """
        logger.info("Checking for articles with incomplete images...")
        
        # Get articles that need image retry
        incomplete_articles = self.db.get_articles_with_incomplete_images(limit=5)
        
        if not incomplete_articles:
            logger.info("No articles with incomplete images found")
            return 0
        
        logger.info(f"Found {len(incomplete_articles)} articles with incomplete images, retrying...")
        retried = 0
        
        for article in incomplete_articles:
            article_id = str(article.get('_id', ''))
            title = article.get('title', 'Unknown')[:40]
            
            # Reset article for retry
            if self.db.mark_article_for_image_retry(article_id):
                logger.info(f"Marked article for retry: {title}")
                
                # Re-fetch the article and process
                articles = self.db.get_articles_for_image_generation(limit=1)
                if articles:
                    result = self.process_article(articles[0])
                    if result:
                        retried += 1
                        logger.info(f"Successfully retried images for: {title}")
        
        return retried
    
    def close(self):
        """Clean up resources."""
        if self.db:
            self.db.disconnect()
            logger.info("Image creation agent closed")


# For running as a standalone script
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("\n" + "="*60)
    print("  IMAGE CREATION AGENT - Standalone Test")
    print("="*60 + "\n")
    
    try:
        agent = ImageCreationAgent()
        
        # Run image generation
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
        import traceback
        traceback.print_exc()
    finally:
        if 'agent' in locals():
            agent.close()
