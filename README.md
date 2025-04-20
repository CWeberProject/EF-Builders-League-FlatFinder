# Craigslist Housing Scraper

A sophisticated web scraper for Craigslist housing listings with advanced anti-detection measures and human-like behavior simulation.

## Features

- Rate limiting with jitter to avoid detection
- Selenium-based contact information extraction with human-like behavior
- Sophisticated browser fingerprinting evasion
- Comprehensive parsing of listing details
- Robust error handling and retries
- Command-line interface

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The scraper can be run from the command line:

```bash
python -m scraper.main [URLs] [-o OUTPUT] [-r RETRIES]
```

### Arguments

- `URLs`: One or more Craigslist housing listing URLs to scrape
- `-o, --output`: Optional output JSON file path (default: print to stdout)
- `-r, --retries`: Maximum number of retry attempts (default: 3)

### Example

```bash
python -m scraper.main "https://sfbay.craigslist.org/sfc/apa/xxx.html" -o results.json
```

## Project Structure

```
scraper/
├── core/
│   ├── scraper.py       # Main scraper implementation
│   └── rate_limiter.py  # Rate limiting functionality
├── parsers/
│   ├── listing_parser.py # Listing details parser
│   └── contact_parser.py # Contact information parser
└── utils/
    ├── browser_config.py # Selenium configuration
    ├── http_utils.py     # HTTP request utilities
    └── logging_config.py # Logging configuration
```

## Data Structure

The scraper returns a JSON object containing:

```json
{
  "breadcrumbs": ["housing", "apts/housing for rent"],
  "title_info": {
    "price": "$2500",
    "housing": "2br - 1000ft²",
    "title": "Modern 2BR Apartment",
    "location": "soma / south beach"
  },
  "attributes": {
    "basic_info": ["2BR / 1Ba"],
    "amenities": ["in-unit laundry", "dishwasher"],
    "property_info": {
      "parking": "attached garage"
    },
    "pets_policy": ["cats are OK", "dogs are OK"],
    "utility_info": {
      "included": ["water", "garbage"],
      "tenant_responsible": ["electricity", "gas"]
    }
  },
  "posting_info": {
    "post_id": "12345678",
    "post_date": "2024-04-19T12:00:00-0700"
  },
  "contact_info": {
    "contact_name": "John Smith",
    "call_number": "415-555-0123",
    "text_number": "415-555-0123",
    "email": "user123@hous.craigslist.org"
  },
  "description": "Detailed listing description...",
  "url": "https://sfbay.craigslist.org/sfc/apa/xxx.html"
}
```

## Error Handling

The scraper includes comprehensive error handling:
- Rate limit detection and backoff
- Automatic retries for failed requests
- Detailed logging
- Graceful degradation when partial data is unavailable

## Notes

- The scraper uses sophisticated anti-detection measures but should be used responsibly
- Respect Craigslist's terms of service and rate limits
- Some listing data may be unavailable if the post is deleted or modified