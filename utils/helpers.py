"""
Utility helper functions for the scraper agent.
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def extract_article_text(url: str, user_agent: str, timeout: int = 10) -> Optional[str]:
    """
    Extract article text from a URL by scraping paragraphs.
    
    Args:
        url: URL of the article to scrape
        user_agent: User agent string for the request
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text or None if failed
    """
    headers = {"User-Agent": user_agent}
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Handle forbidden responses
        if response.status_code == 403:
            logger.warning(f"Forbidden (403): {url}")
            return None
        
        if response.status_code != 200:
            logger.warning(f"HTTP {response.status_code}: {url}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract text from paragraphs
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)
        
        # Clean up text
        text = clean_text(text)
        
        if len(text) < 100:
            logger.debug(f"Insufficient content extracted from: {url}")
            return None
            
        return text
        
    except requests.Timeout:
        logger.warning(f"Timeout fetching: {url}")
        return None
    except requests.RequestException as e:
        logger.warning(f"Request failed for {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error extracting from {url}: {e}")
        return None


def clean_text(text: str) -> str:
    """
    Clean and sanitize extracted text.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    # Remove problematic characters
    text = text.replace("'", "'")
    text = text.replace("\\", "")
    text = text.replace("\xa0", " ")
    text = text.replace("\n", " ")
    text = text.replace("\r", "")
    
    # Remove multiple spaces
    while "  " in text:
        text = text.replace("  ", " ")
    
    return text.strip()


def parse_datetime(date_string: str) -> Optional[datetime]:
    """
    Parse various datetime formats.
    
    Args:
        date_string: Date string to parse
        
    Returns:
        Parsed datetime or None if failed
    """
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date: {date_string}")
    return None
