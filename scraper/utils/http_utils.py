import requests
from urllib.parse import urlparse
from typing import Optional, Dict, Any
import time
from .logging_config import logger
from .browser_config import get_random_user_agent

def validate_url(url: str) -> bool:
    """Validate if the URL is a proper Craigslist housing listing URL."""
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ('http', 'https') and
            'craigslist.org' in parsed.netloc and
            parsed.path
        )
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return False

def make_request(url: str, session: requests.Session, retry_count: int = 0, max_retries: int = 3) -> Optional[str]:
    """Make HTTP request with error handling and retries."""
    if not validate_url(url):
        raise ValueError("Invalid Craigslist URL provided")
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text

    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:  # Too Many Requests
            if retry_count < max_retries:
                logger.warning("Rate limit exceeded, waiting longer...")
                time.sleep(60 * (retry_count + 1))  # Exponential backoff
                return make_request(url, session, retry_count + 1, max_retries)
        logger.error(f"HTTP error occurred: {e}")

    except (requests.exceptions.RequestException, Exception) as e:
        if retry_count < max_retries:
            logger.warning(f"Request failed, retrying ({retry_count + 1}/{max_retries})...")
            time.sleep(5 * (retry_count + 1))  # Exponential backoff
            return make_request(url, session, retry_count + 1, max_retries)
        logger.error(f"Error fetching URL: {e}")

    return None

def create_session() -> requests.Session:
    """Create a session with default configuration."""
    return requests.Session()