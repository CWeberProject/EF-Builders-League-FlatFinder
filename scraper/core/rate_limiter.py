import time
import random
from ..utils.logging_config import logger

class RateLimiter:
    """Token bucket algorithm for rate limiting with jitter."""
    
    def __init__(self, min_delay: float = 5.0, max_delay: float = 10.0):
        """Initialize rate limiter with configurable delays.
        
        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        logger.info(f"Rate limiter initialized with delays: {min_delay}-{max_delay}s")

    def wait(self):
        """Wait for appropriate delay with jitter between min and max delay."""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            delay = random.uniform(self.min_delay, self.max_delay)
            
            if elapsed < delay:
                wait_time = delay - elapsed
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                time.sleep(wait_time)
        
        self.last_request_time = time.time()