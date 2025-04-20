from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver

from ..utils.logging_config import logger
from ..utils.browser_config import setup_webdriver
from ..utils.http_utils import make_request, create_session
from .rate_limiter import RateLimiter
from ..parsers.listing_parser import ListingParser
from ..parsers.contact_parser import ContactParser

class CraigslistScraper:
    """Scraper for Craigslist housing listings with error handling and rate limiting."""
    
    def __init__(self, max_retries: int = 3):
        """Initialize the scraper with configurable retry attempts.
        
        Args:
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.session = create_session()
        self.rate_limiter = RateLimiter()
        self.max_retries = max_retries
        self.driver: Optional[WebDriver] = None
        logger.info("CraigslistScraper initialized")

    def __del__(self):
        """Clean up resources on object destruction."""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")

    def _ensure_driver(self):
        """Ensure Selenium WebDriver is initialized."""
        if not self.driver:
            self.driver = setup_webdriver()

    def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape listing information from a Craigslist URL.
        
        Args:
            url: The URL of the Craigslist housing listing to scrape
            
        Returns:
            Dictionary containing the scraped listing data, or None if scraping failed
        """
        try:
            logger.info(f"Starting scrape for URL: {url}")
            
            # Apply rate limiting
            self.rate_limiter.wait()
            
            # Get the listing HTML
            html_content = make_request(url, self.session, max_retries=self.max_retries)
            if not html_content:
                logger.error("Failed to fetch listing HTML")
                return None
                
            # Parse listing details
            listing_parser = ListingParser()
            listing_data = listing_parser.parse_listing(html_content)
            
            # Initialize Selenium for contact info
            self._ensure_driver()
            contact_parser = ContactParser(self.driver)
            
            # Get contact information
            contact_info = contact_parser.extract_contact_info(url)
            
            # Combine all data
            data = {
                **listing_data,
                'contact_info': contact_info,
                'url': url
            }
            
            logger.info("Successfully scraped listing")
            return data

        except Exception as e:
            logger.error(f"Error scraping listing: {e}")
            return None