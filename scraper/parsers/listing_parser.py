from typing import Dict, Any, List
from bs4 import BeautifulSoup
from ..utils.logging_config import logger

class ListingParser:
    """Parser for extracting listing details from Craigslist housing posts."""

    @staticmethod
    def parse_breadcrumbs(soup: BeautifulSoup) -> List[str]:
        """Extract category hierarchy from breadcrumbs."""
        breadcrumbs = []
        for crumb in soup.select('.breadcrumbs .crumb'):
            link = crumb.find('a')
            if link:
                breadcrumbs.append(link.text.strip())
        return breadcrumbs

    @staticmethod
    def parse_title_info(soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract information from the title section."""
        title_section = soup.select_one('.postingtitletext')
        if not title_section:
            return {}
        
        result = {
            'price': None,
            'housing': None,
            'title': None,
            'location': None
        }

        price = title_section.select_one('.price')
        if price:
            result['price'] = price.text.strip()

        housing = title_section.select_one('.housing')
        if housing:
            result['housing'] = housing.text.strip()

        title = title_section.select_one('#titletextonly')
        if title:
            result['title'] = title.text.strip()

        location = title_section.find(string=lambda t: t and '(' in t and ')' in t)
        if location:
            result['location'] = location.strip('() ')

        return result

    @staticmethod
    def parse_attributes(soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract listing attributes."""
        attrs = {
            'basic_info': [],
            'amenities': [],
            'open_house_dates': [],
            'property_info': {},
            'pets_policy': [],
            'utility_info': {
                'included': [],
                'tenant_responsible': []
            }
        }
        
        # Basic attributes
        for span in soup.select('.attrgroup span.attr'):
            text = span.text.strip()
            if text:
                # Skip if it's an open house label
                if 'open house dates:' in text.lower():
                    continue
                    
                # Parse pets policy
                if 'cats are OK' in text or 'dogs are OK' in text:
                    attrs['pets_policy'].append(text)
                # Parse parking
                elif 'parking' in text.lower():
                    attrs['property_info']['parking'] = text
                # Parse other amenities
                else:
                    attrs['amenities'].append(text)

        # Open house dates
        for div in soup.select('.attrgroup div.attr'):
            if 'open house' in div.text.lower():
                date = div.select_one('.valu')
                if date:
                    attrs['open_house_dates'].append(date.text.strip())

        # Basic info (bedrooms, availability)
        basic_info = soup.select_one('.attrgroup span.shared-line-bubble')
        if basic_info:
            attrs['basic_info'].append(basic_info.text.strip())

        return {k: v for k, v in attrs.items() if v}

    @staticmethod
    def parse_posting_info(soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract posting information (ID, date, etc)."""
        info = {}
        
        post_id = soup.select_one('.postinginfo:-soup-contains("post id")')
        if post_id:
            info['post_id'] = post_id.text.replace('post id:', '').strip()

        post_time = soup.select_one('time.date')
        if post_time:
            info['post_date'] = post_time.get('datetime')

        updated_time = soup.select_one('.timeago')
        if updated_time:
            info['updated_date'] = updated_time.get('datetime')

        return info

    @staticmethod
    def parse_description(soup: BeautifulSoup) -> str:
        """Extract the listing description."""
        description = soup.select_one('#postingbody')
        if description:
            # Remove "QR Code Link to This Post" text
            qr_section = description.find('a', string='QR Code Link to This Post')
            if qr_section:
                qr_section.decompose()
            return description.text.strip()
        return ""

    @classmethod
    def parse_listing(cls, html: str) -> Dict[str, Any]:
        """Parse all listing information from HTML content."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            return {
                'breadcrumbs': cls.parse_breadcrumbs(soup),
                'title_info': cls.parse_title_info(soup),
                'attributes': cls.parse_attributes(soup),
                'posting_info': cls.parse_posting_info(soup),
                'description': cls.parse_description(soup)
            }
            
        except Exception as e:
            logger.error(f"Error parsing listing HTML: {e}")
            return {}