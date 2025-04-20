import argparse
import json
from typing import List, Dict, Any
import sys

from scraper.core.scraper import CraigslistScraper
from scraper.utils.logging_config import logger

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape Craigslist housing listings with sophisticated anti-detection."
    )
    
    parser.add_argument(
        'urls',
        nargs='+',
        help='One or more Craigslist housing listing URLs to scrape'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file path (default: print to stdout)',
        default=None
    )
    
    parser.add_argument(
        '-r', '--retries',
        help='Maximum number of retry attempts (default: 0)',
        type=int,
        default=0
    )
    
    return parser.parse_args()

def save_results(results: List[Dict[str, Any]], output_path: str = None):
    """Save scraping results to file or print to stdout."""
    json_data = json.dumps(results, indent=2)
    
    if output_path:
        try:
            with open(output_path, 'w') as f:
                f.write(json_data)
            logger.info(f"Results saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving results to file: {e}")
            print(json_data)
    else:
        print(json_data)

def main():
    """Main entry point for the scraper."""
    args = parse_args()
    
    try:
        # Initialize scraper
        scraper = CraigslistScraper(max_retries=args.retries)
        results = []
        
        # Process each URL
        for url in args.urls:
            logger.info(f"Processing URL: {url}")
            result = scraper.scrape(url)
            
            if result:
                results.append(result)
            else:
                logger.warning(f"No data obtained for URL: {url}")
        
        # Save or print results
        save_results(results, args.output)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())