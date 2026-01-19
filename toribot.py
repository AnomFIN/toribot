#!/usr/bin/env python3
"""
Toribot - A bot for monitoring new products on Tori.fi
Polls the Tori.fi search page every 60 seconds and stores new product information.
"""

import re
import json
import time
import logging
import os
from html import unescape
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


# Configuration
SEARCH_URL = "https://www.tori.fi/recommerce/forsale/search?sort=PUBLISHED_DESC&trade_type=2"
PRODUCTS_FILE = "products.json"
POLL_INTERVAL = 60  # seconds
SERVER_PORT = 8000

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductStorage:
    """Handles loading and saving product data."""
    
    def __init__(self, filename):
        self.filename = filename
        self.products = self._load_products()
    
    def _load_products(self):
        """Load products from JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading products: {e}")
                return []
        return []
    
    def save_products(self):
        """Save products to JSON file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.products)} products to {self.filename}")
        except IOError as e:
            logger.error(f"Error saving products: {e}")
    
    def add_product(self, product):
        """Add a new product if it doesn't exist."""
        if not self.product_exists(product['id']):
            self.products.insert(0, product)  # Add to beginning for newest first
            return True
        return False
    
    def product_exists(self, product_id):
        """Check if a product ID already exists."""
        return any(p['id'] == product_id for p in self.products)
    
    def get_all_ids(self):
        """Get all stored product IDs."""
        return {p['id'] for p in self.products}


class ToriFetcher:
    """Handles fetching and parsing data from Tori.fi."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_page(self, url):
        """Fetch a web page and return its content."""
        try:
            request = Request(url, headers=self.headers)
            with urlopen(request, timeout=10) as response:
                return response.read().decode('utf-8')
        except (URLError, HTTPError) as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_product_links(self, html):
        """Extract product IDs from the search page."""
        if not html:
            return []
        
        # Match URLs like /recommerce/forsale/item/<id>
        pattern = r'/recommerce/forsale/item/(\d+)'
        matches = re.findall(pattern, html)
        
        # Return unique IDs
        return list(set(matches))
    
    def fetch_product_details(self, product_id):
        """Fetch detailed information for a product."""
        url = f"https://www.tori.fi/recommerce/forsale/item/{product_id}"
        html = self.fetch_page(url)
        
        if not html:
            return None
        
        product = {
            'id': product_id,
            'url': url,
            'title': self._extract_title(html),
            'description': self._extract_description(html),
            'location': self._extract_location(html),
            'seller': self._extract_seller(html),
            'image_url': self._extract_image(html),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return product
    
    def _extract_title(self, html):
        """Extract product title from HTML."""
        match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
        if match:
            return self._clean_text(match.group(1))
        return "N/A"
    
    def _extract_description(self, html):
        """Extract product description from HTML."""
        # Try to find description in various common patterns
        patterns = [
            r'<meta\s+property="og:description"\s+content="([^"]*)"',
            r'<meta\s+name="description"\s+content="([^"]*)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        
        return "N/A"
    
    def _extract_location(self, html):
        """Extract location from HTML."""
        # Look for location patterns
        patterns = [
            r'location["\']?\s*:\s*["\']([^"\']+)["\']',
            r'Sijainti[:\s]+([^<]+)<',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        
        return "N/A"
    
    def _extract_seller(self, html):
        """Extract seller name from HTML."""
        patterns = [
            r'seller["\']?\s*:\s*["\']([^"\']+)["\']',
            r'Myyjä[:\s]+([^<]+)<',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        
        return "N/A"
    
    def _extract_image(self, html):
        """Extract image URL from HTML."""
        patterns = [
            r'<meta\s+property="og:image"\s+content="([^"]*)"',
            r'<img[^>]+src="(https://[^"]*tori[^"]*)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _clean_text(self, text):
        """Clean extracted text by removing HTML tags and extra whitespace."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities using standard library
        text = unescape(text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()


class ToriBot:
    """Main bot that coordinates polling and storage."""
    
    def __init__(self):
        self.storage = ProductStorage(PRODUCTS_FILE)
        self.fetcher = ToriFetcher()
        self.running = False
    
    def poll_once(self):
        """Perform one polling cycle."""
        logger.info("Polling Tori.fi for new products...")
        
        # Fetch the search page
        html = self.fetcher.fetch_page(SEARCH_URL)
        if not html:
            logger.warning("Failed to fetch search page")
            return
        
        # Extract product IDs
        product_ids = self.fetcher.extract_product_links(html)
        logger.info(f"Found {len(product_ids)} product links")
        
        # Check for new products
        new_count = 0
        for product_id in product_ids:
            if not self.storage.product_exists(product_id):
                logger.info(f"New product found: {product_id}")
                
                # Fetch detailed information
                product = self.fetcher.fetch_product_details(product_id)
                if product:
                    self.storage.add_product(product)
                    new_count += 1
                    logger.info(f"Added product: {product['title']}")
                
                # Small delay to avoid hammering the server
                time.sleep(1)
        
        if new_count > 0:
            self.storage.save_products()
            logger.info(f"Added {new_count} new products")
        else:
            logger.info("No new products found")
    
    def start_polling(self):
        """Start the polling loop."""
        self.running = True
        logger.info(f"Starting polling loop (interval: {POLL_INTERVAL}s)")
        
        # Do initial poll
        self.poll_once()
        
        while self.running:
            time.sleep(POLL_INTERVAL)
            self.poll_once()
    
    def stop_polling(self):
        """Stop the polling loop."""
        self.running = False
        logger.info("Polling stopped")


def start_http_server(port=SERVER_PORT):
    """Start a simple HTTP server to serve the GUI."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    logger.info(f"HTTP server running at http://localhost:{port}")
    httpd.serve_forever()


def main():
    """Main entry point."""
    logger.info("Starting ToriBot...")
    
    # Initialize the bot
    bot = ToriBot()
    
    # Start HTTP server in a separate thread
    server_thread = Thread(target=start_http_server, daemon=True)
    server_thread.start()
    
    try:
        # Start polling (blocks)
        bot.start_polling()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        bot.stop_polling()


if __name__ == "__main__":
    main()
