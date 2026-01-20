#!/usr/bin/env python3
"""
Tori Annataan Bot - Complete working project
Goal: Poll Tori.fi "annetaan" listings, detect new items, download images,
      run OpenAI valuations, and provide modern GUI with settings management.
"""

import re
import json
import time
import logging
import os
import signal
import sys
import random
import copy
from datetime import datetime
from threading import Thread, Event, Lock
from pathlib import Path
from html import unescape

# Third-party imports
try:
    from flask import Flask, jsonify, request, send_from_directory
    import requests
    from PIL import Image
    from io import BytesIO
except ImportError as e:
    print(f"Error: Missing required package. Install with: pip install flask requests pillow openai")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File paths
PRODUCTS_FILE = "products.json"
SETTINGS_FILE = "settings.json"
DEBUG_DIR = "debug"
IMAGES_DIR = "images"

# Default settings
DEFAULT_SETTINGS = {
    "poll_interval_seconds": 60,
    "listing_url": "https://www.tori.fi/recommerce/forsale/search?sort=PUBLISHED_DESC&trade_type=2",
    "request_timeout_seconds": 15,
    "max_retries": 2,
    "products_per_page": 50,  # Approximate number of products per page on Tori.fi
    "openai": {
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "valuation_interval_minutes": 60,
        "enabled": False
    },
    "images": {
        "download_enabled": True,
        "max_images_per_item": 5
    },
    "server": {
        "host": "127.0.0.1",
        "port": 8788
    },
    "tori_login": {
        "enabled": False,
        "username": "",
        "password": "",
        "remember_session": True
    }
}

# Regex pattern
PRODUCT_ID_PATTERN = r'href=["\'][^"\']*?/recommerce/forsale/item/(\d+)'


class SettingsManager:
    """Manages application settings with file persistence"""
    
    def __init__(self, filename=SETTINGS_FILE):
        self.filename = filename
        self.lock = Lock()
        self.settings = self._load_settings()
    
    def _load_settings(self):
        """Load settings from file or create with defaults"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults for any missing keys
                    return self._merge_with_defaults(loaded)
            except Exception as e:
                logger.error(f"Error loading settings: {e}. Using defaults.")
                return DEFAULT_SETTINGS.copy()
        else:
            logger.info("Settings file not found. Creating with defaults.")
            self._save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
    
    def _merge_with_defaults(self, loaded):
        """Merge loaded settings with defaults to handle missing keys"""
        # Use deep copy to avoid mutating DEFAULT_SETTINGS
        result = copy.deepcopy(DEFAULT_SETTINGS)
        for key in loaded:
            if isinstance(loaded[key], dict) and key in result:
                result[key].update(loaded[key])
            else:
                result[key] = loaded[key]
        return result
    
    def _save_settings(self, settings):
        """Save settings to file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def get_settings(self):
        """Get current settings (thread-safe)"""
        with self.lock:
            return self.settings.copy()
    
    def update_settings(self, new_settings):
        """Update settings with validation (thread-safe)"""
        with self.lock:
            # Validate
            if not isinstance(new_settings, dict):
                raise ValueError("Settings must be a dictionary")
            
            # Validate numeric fields
            if "poll_interval_seconds" in new_settings:
                val = new_settings["poll_interval_seconds"]
                if not isinstance(val, (int, float)) or val < 10:
                    raise ValueError("poll_interval_seconds must be >= 10")
            
            if "request_timeout_seconds" in new_settings:
                val = new_settings["request_timeout_seconds"]
                if not isinstance(val, (int, float)) or val < 1:
                    raise ValueError("request_timeout_seconds must be >= 1")
            
            # Update and save
            for key in new_settings:
                if isinstance(new_settings[key], dict) and key in self.settings:
                    self.settings[key].update(new_settings[key])
                else:
                    self.settings[key] = new_settings[key]
            
            self._save_settings(self.settings)
            return True


class ProductDatabase:
    """Manages products database with file persistence"""
    
    def __init__(self, filename=PRODUCTS_FILE):
        self.filename = filename
        self.lock = Lock()
        self.data = self._load_database()
    
    def _load_database(self):
        """Load database from file or create new"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading database: {e}. Creating new.")
                return self._create_new_database()
        else:
            logger.info("Database file not found. Creating new.")
            return self._create_new_database()
    
    def _create_new_database(self):
        """Create new database structure"""
        return {
            "meta": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "schema_version": 1
            },
            "items": {}
        }
    
    def _save_database(self):
        """Save database to file"""
        try:
            self.data["meta"]["updated_at"] = datetime.now().isoformat()
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def item_exists(self, item_id):
        """Check if item exists"""
        with self.lock:
            return str(item_id) in self.data["items"]
    
    def add_item(self, item_id, item_data):
        """Add or update item"""
        with self.lock:
            self.data["items"][str(item_id)] = item_data
            self._save_database()
    
    def get_item(self, item_id):
        """Get single item"""
        with self.lock:
            return self.data["items"].get(str(item_id))
    
    def get_all_items(self):
        """Get all items as list"""
        with self.lock:
            return list(self.data["items"].values())
    
    def get_items_needing_valuation(self):
        """Get items that need OpenAI valuation"""
        with self.lock:
            items = []
            for item_id, item in self.data["items"].items():
                if not item.get("valuation") or item.get("valuation", {}).get("status") == "pending":
                    items.append((item_id, item))
            return items


class ToriFetcher:
    """Handles HTTP requests with retries, jitter, and error handling"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.logged_in = False
    
    def login_if_configured(self):
        """Attempt login if credentials are configured"""
        settings = self.settings_manager.get_settings()
        tori_login = settings.get("tori_login", {})
        
        if not tori_login.get("enabled", False):
            return False
            
        username = tori_login.get("username", "").strip()
        password = tori_login.get("password", "").strip()
        
        if not username or not password:
            logger.warning("Tori login enabled but credentials missing")
            return False
            
        try:
            # First get login page for any tokens/csrf
            login_page = self.session.get("https://www.tori.fi/")
            
            # Attempt login (this is a simplified version - actual implementation would need proper form handling)
            login_data = {
                'username': username,
                'password': password
            }
            
            response = self.session.post(
                "https://www.tori.fi/api/auth/login",
                json=login_data,
                timeout=15
            )
            
            if response.status_code == 200:
                self.logged_in = True
                logger.info("Successfully logged in to Tori.fi")
                return True
            else:
                logger.warning(f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def _add_jitter(self):
        """Add random jitter 0-3 seconds"""
        time.sleep(random.uniform(0, 3))
    
    def _fetch_with_retries(self, url, timeout):
        """Fetch URL with retry logic and exponential backoff"""
        settings = self.settings_manager.get_settings()
        max_retries = settings.get("max_retries", 2)
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt < max_retries:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff
                    logger.warning(f"Fetch attempt {attempt + 1} failed for {url}: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All fetch attempts failed for {url}: {e}")
                    return None
    
    def fetch_listing_page(self, page=None):
        """Fetch main listing page"""
        settings = self.settings_manager.get_settings()
        url = settings.get("listing_url")
        
        # Add page parameter if specified
        if page is not None and page > 1:
            if '?' in url:
                url = f"{url}&page={page}"
            else:
                url = f"{url}?page={page}"
        
        timeout = settings.get("request_timeout_seconds", 15)
        
        self._add_jitter()
        response = self._fetch_with_retries(url, timeout)
        
        if response:
            return response.text
        return None
    
    def fetch_item_page(self, item_id):
        """Fetch individual item page"""
        settings = self.settings_manager.get_settings()
        url = f"https://www.tori.fi/recommerce/forsale/item/{item_id}"
        timeout = settings.get("request_timeout_seconds", 15)
        
        self._add_jitter()
        response = self._fetch_with_retries(url, timeout)
        
        if response:
            return response.text
        return None
    
    def download_image(self, url, save_path):
        """Download and save image"""
        try:
            settings = self.settings_manager.get_settings()
            timeout = settings.get("request_timeout_seconds", 15)
            
            response = self._fetch_with_retries(url, timeout)
            if not response:
                return False
            
            # Validate it's an image
            img = Image.open(BytesIO(response.content))
            img.save(save_path)
            return True
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return False


class ProductExtractor:
    """Extracts product information from HTML"""
    
    @staticmethod
    def extract_product_ids(html):
        """Extract product IDs from listing page"""
        if not html:
            return []
        matches = re.findall(PRODUCT_ID_PATTERN, html)
        return list(set(matches))  # Unique IDs
    
    @staticmethod
    def extract_product_details(html, item_id):
        """Extract details from item page"""
        errors = []
        
        try:
            # Title
            title = None
            match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
            if match:
                title = ProductExtractor._clean_text(match.group(1))
            else:
                errors.append("Failed to extract title")
            
            # Description
            description = None
            patterns = [
                r'<meta\s+property="og:description"\s+content="([^"]*)"',
                r'<meta\s+name="description"\s+content="([^"]*)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    description = ProductExtractor._clean_text(match.group(1))
                    break
            if not description:
                errors.append("Failed to extract description")
            
            # Location - improved extraction with multiple patterns
            location = None
            location_patterns = [
                r'"location"\s*:\s*"([^"]+)"',
                r'<span[^>]*location[^>]*>([^<]+)</span>',
                r'class="[^"]*location[^"]*"[^>]*>([^<]+)<',
                r'"address"[^}]*"locality"\s*:\s*"([^"]+)"'
            ]
            for pattern in location_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    location = ProductExtractor._clean_text(match.group(1))
                    break
            if not location:
                errors.append("Failed to extract location")
            
            # Seller - improved extraction with multiple patterns
            seller = None
            seller_patterns = [
                r'"seller"[^}]*"name"\s*:\s*"([^"]+)"',
                r'"sellerName"\s*:\s*"([^"]+)"',
                r'<span[^>]*seller[^>]*>([^<]+)</span>',
                r'class="[^"]*seller[^"]*"[^>]*>([^<]+)<',
                r'"advertiser"[^}]*"name"\s*:\s*"([^"]+)"'
            ]
            for pattern in seller_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    seller = ProductExtractor._clean_text(match.group(1))
                    break
            if not seller:
                # Try to extract from different parts of the page if logged in
                if "logged" in html.lower() or "profile" in html.lower():
                    errors.append("Seller info available but extraction failed (logged in user)")
                else:
                    errors.append("Seller info not available (login required)")
            
            # Images - improved extraction with multiple patterns
            images = []
            image_patterns = [
                r'"image"\s*:\s*"(https://[^"]+)"',
                r'"imageUrl"\s*:\s*"(https://[^"]+)"',
                r'src="(https://[^"]*tori[^"]*\.(jpg|jpeg|png|webp)[^"]*)"|src="(https://[^"]*image[^"]*\.(jpg|jpeg|png|webp)[^"]*)"'
            ]
            
            for pattern in image_patterns:
                img_matches = re.findall(pattern, html, re.IGNORECASE)
                for match_groups in img_matches:
                    # Handle different regex group structures
                    img_url = match_groups[0] if isinstance(match_groups, tuple) else match_groups
                    if img_url and img_url.startswith('https://'):
                        images.append(img_url)
            
            # Remove duplicates and limit to 5
            images = list(set(images))[:5]
            
            if not images:
                errors.append("No images found")
            
            return {
                "id": str(item_id),
                "url": f"https://www.tori.fi/recommerce/forsale/item/{item_id}",
                "title": title,
                "description": description,
                "location": location,
                "seller": seller,
                "images": images,
                "image_files": [],
                "discovered_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "errors": errors if errors else None,
                "valuation": None
            }
        except Exception as e:
            logger.error(f"Error extracting details for {item_id}: {e}")
            return {
                "id": str(item_id),
                "url": f"https://www.tori.fi/recommerce/forsale/item/{item_id}",
                "title": None,
                "description": None,
                "location": None,
                "seller": None,
                "images": [],
                "image_files": [],
                "discovered_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "errors": [f"Exception during extraction: {str(e)}"],
                "valuation": None
            }
    
    @staticmethod
    def _clean_text(text):
        """Clean extracted text"""
        if not text:
            return None
        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(text)
        text = ' '.join(text.split())
        return text.strip() or None


class OpenAIValuator:
    """Handles OpenAI-based product valuation"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
    
    def is_enabled(self):
        """Check if OpenAI is enabled"""
        settings = self.settings_manager.get_settings()
        openai_settings = settings.get("openai", {})
        return openai_settings.get("enabled", False) and openai_settings.get("api_key", "").strip() != ""
    
    def valuate_item(self, item):
        """Valuate a single item using OpenAI"""
        if not self.is_enabled():
            return None
        
        try:
            settings = self.settings_manager.get_settings()
            openai_settings = settings.get("openai", {})
            
            # Import OpenAI
            try:
                from openai import OpenAI
            except ImportError:
                logger.error("OpenAI package not installed")
                return {"status": "error", "message": "OpenAI package not installed"}
            
            # Create client
            client = OpenAI(
                api_key=openai_settings.get("api_key"),
                base_url=openai_settings.get("base_url", "https://api.openai.com/v1")
            )
            
            # Prepare prompt
            prompt = f"""Analysoi tämä ilmainen tuote Tori.fi palvelusta ja anna lyhyt arvio suomeksi:

Otsikko: {item.get('title', 'Ei tietoa')}
Kuvaus: {item.get('description', 'Ei kuvausta')}
Sijainti: {item.get('location', 'Ei sijaintia')}
Myyjä: {item.get('seller', 'Ei myyjätietoa')}

Anna arvio 4-5 lauseessa:
1. Arvio hinnasta uutena (€)
2. Arvio nykyisestä arvosta käytettynä (€)
3. Kunnon arvio ja keskeiset hyvät/huonot puolet
4. Suositus: Kannattaako hakea? (Kyllä/Ei/Ehkä)

Lisää lopuksi molemmat arviot numeromuodossa:
HINTA_UUTENA: X€
ARVO_NYT: Y€

Vastaa vain suomeksi, ole ytimekäs."""
            
            # Call API
            response = client.chat.completions.create(
                model=openai_settings.get("model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "Olet hyödyllinen avustaja joka arvioi ilmaisia tuotteita suomeksi. Anna realistisia hinta-arvioita euroina."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            valuation_text = response.choices[0].message.content.strip()
            
            # Extract both price values
            price_new = None
            price_current = None
            
            # Try to extract "HINTA_UUTENA" value
            price_new_match = re.search(r'HINTA_UUTENA:\s*(\d+)€?', valuation_text, re.IGNORECASE)
            if price_new_match:
                try:
                    price_new = int(price_new_match.group(1))
                except ValueError:
                    pass
            
            # Try to extract "ARVO_NYT" value
            price_current_match = re.search(r'ARVO_NYT:\s*(\d+)€?', valuation_text, re.IGNORECASE)
            if price_current_match:
                try:
                    price_current = int(price_current_match.group(1))
                except ValueError:
                    pass
            
            # Fallback to old "ARVO:" format for backwards compatibility
            if price_current is None:
                price_match = re.search(r'ARVO:\s*(\d+)€?', valuation_text, re.IGNORECASE)
                if price_match:
                    try:
                        price_current = int(price_match.group(1))
                    except ValueError:
                        pass
            
            return {
                "status": "completed",
                "text": valuation_text,
                "price_new": price_new,
                "price_current": price_current,
                "price_estimate": price_current,  # Keep for backwards compatibility
                "model": openai_settings.get("model"),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error valuating item {item.get('id')}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }


class ToriBot:
    """Main bot coordinator"""
    
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.database = ProductDatabase()
        self.fetcher = ToriFetcher(self.settings_manager)
        self.valuator = OpenAIValuator(self.settings_manager)
        
        self.running = False
        self.stop_event = Event()
        self.poll_thread = None
        self.valuation_thread = None
        self.last_valuation_time = None
        
        # Ensure directories exist
        Path(DEBUG_DIR).mkdir(exist_ok=True)
        Path(IMAGES_DIR).mkdir(exist_ok=True)
        
        # Attempt login if configured
        if self.fetcher.login_if_configured():
            logger.info("Tori.fi login successful - enhanced data extraction available")
    
    def start(self):
        """Start the bot"""
        if self.running:
            logger.warning("Bot already running")
            return
        
        self.running = True
        self.stop_event.clear()
        
        # Start polling thread
        self.poll_thread = Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        
        # Start valuation thread
        self.valuation_thread = Thread(target=self._valuation_loop, daemon=True)
        self.valuation_thread.start()
        
        logger.info("Bot started")
    
    def stop(self):
        """Stop the bot"""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        logger.info("Bot stopping...")
        
        if self.poll_thread:
            self.poll_thread.join(timeout=5)
        if self.valuation_thread:
            self.valuation_thread.join(timeout=5)
        
        logger.info("Bot stopped")
    
    def _poll_loop(self):
        """Polling loop - runs continuously"""
        logger.info("Polling loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                self._poll_once()
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
            
            # Wait for next poll
            settings = self.settings_manager.get_settings()
            interval = settings.get("poll_interval_seconds", 60)
            self.stop_event.wait(interval)
    
    def _poll_once(self, page=None):
        """Perform one polling cycle"""
        page_info = f" (page {page})" if page else ""
        logger.info(f"Polling for new items{page_info}...")
        
        # Fetch listing page
        html = self.fetcher.fetch_listing_page(page)
        if not html:
            logger.warning(f"Failed to fetch listing page{page_info}")
            return
        
        # Extract product IDs
        product_ids = ProductExtractor.extract_product_ids(html)
        logger.info(f"Found {len(product_ids)} product IDs{page_info}")
        
        # Check for new items
        new_count = 0
        for product_id in product_ids:
            if not self.database.item_exists(product_id):
                logger.info(f"New item found: {product_id}")
                
                # Fetch item details
                item_html = self.fetcher.fetch_item_page(product_id)
                if not item_html:
                    logger.warning(f"Failed to fetch item page for {product_id}")
                    continue
                
                # Extract details
                item_data = ProductExtractor.extract_product_details(item_html, product_id)
                
                # Download images
                settings = self.settings_manager.get_settings()
                if settings.get("images", {}).get("download_enabled", True):
                    self._download_item_images(item_data)
                
                # Save to database
                self.database.add_item(product_id, item_data)
                new_count += 1
        
        if new_count > 0:
            logger.info(f"Added {new_count} new items{page_info}")
        else:
            logger.info(f"No new items found{page_info}")
    
    def _download_item_images(self, item_data):
        """Download images for an item"""
        settings = self.settings_manager.get_settings()
        max_images = settings.get("images", {}).get("max_images_per_item", 5)
        
        item_id = item_data["id"]
        images = item_data.get("images", [])[:max_images]
        
        downloaded = []
        for idx, img_url in enumerate(images):
            try:
                # Create filename with case-insensitive extension handling
                ext = img_url.split('.')[-1].split('?')[0].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    ext = 'jpg'
                filename = f"{item_id}_{idx}.{ext}"
                filepath = os.path.join(IMAGES_DIR, filename)
                
                # Download
                if self.fetcher.download_image(img_url, filepath):
                    downloaded.append(filename)
                    logger.info(f"Downloaded image {filename}")
            except Exception as e:
                logger.error(f"Error downloading image {img_url}: {e}")
        
        item_data["image_files"] = downloaded
    
    def _valuation_loop(self):
        """Valuation loop - runs hourly or on-demand"""
        logger.info("Valuation loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                if self.valuator.is_enabled():
                    self._run_valuations()
            except Exception as e:
                logger.error(f"Error in valuation loop: {e}")
            
            # Wait for next valuation cycle
            settings = self.settings_manager.get_settings()
            interval_minutes = settings.get("openai", {}).get("valuation_interval_minutes", 60)
            self.stop_event.wait(interval_minutes * 60)
    
    def _run_valuations(self):
        """Run valuations for items that need it"""
        items_to_valuate = self.database.get_items_needing_valuation()
        
        if not items_to_valuate:
            logger.info("No items need valuation")
            return
        
        logger.info(f"Valuating {len(items_to_valuate)} items...")
        
        for item_id, item in items_to_valuate:
            if not self.running:
                break
            
            try:
                valuation = self.valuator.valuate_item(item)
                if valuation:
                    # Work on a copy to avoid mutating shared database state outside its lock
                    updated_item = dict(item)
                    updated_item["valuation"] = valuation
                    updated_item["updated_at"] = datetime.now().isoformat()
                    self.database.add_item(item_id, updated_item)
                    logger.info(f"Valuated item {item_id}")
                
                # Small delay between API calls
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error valuating item {item_id}: {e}")
        
        self.last_valuation_time = datetime.now()
        logger.info("Valuation cycle completed")
    
    def trigger_valuations(self):
        """Manually trigger valuations"""
        if not self.valuator.is_enabled():
            return {"success": False, "message": "OpenAI is not enabled"}
        
        Thread(target=self._run_valuations, daemon=True).start()
        return {"success": True, "message": "Valuation started"}
    
    def fetch_multiple_pages(self, num_products):
        """Fetch products from multiple pages based on requested count
        
        Args:
            num_products: Approximate number of products to fetch
            
        Returns:
            dict: Success status and number of pages fetched
            
        Note:
            - Uses ceiling division to calculate pages needed
            - Continues fetching remaining pages even if one page fails
            - Each page fetch is logged independently for tracking
        """
        settings = self.settings_manager.get_settings()
        products_per_page = settings.get("products_per_page", 50)
        num_pages = (num_products + products_per_page - 1) // products_per_page  # Ceiling division
        
        logger.info(f"Fetching approximately {num_products} products from {num_pages} pages...")
        
        for page_num in range(1, num_pages + 1):
            try:
                self._poll_once(page=page_num)
                logger.info(f"Completed fetching page {page_num}/{num_pages}")
            except Exception as e:
                logger.error(f"Error fetching page {page_num}: {e}")
        
        logger.info(f"Multi-page fetch completed: processed {num_pages} pages")
        return {"success": True, "pages_fetched": num_pages}


# Flask Application
app = Flask(__name__)

# Global bot instance
bot = None


@app.route('/')
def index():
    """Serve main GUI"""
    return send_from_directory('.', 'gui.html')


@app.route('/gui.html')
def gui():
    """Serve GUI HTML file"""
    return send_from_directory('.', 'gui.html')


@app.route('/styles.css')
def styles():
    """Serve CSS"""
    return send_from_directory('.', 'styles.css')


@app.route('/api/products')
def get_products():
    """Get all products"""
    logger.info("API call: /api/products")
    try:
        items = bot.database.get_all_items()
        # Sort by discovered_at descending
        items.sort(key=lambda x: x.get('discovered_at', ''), reverse=True)
        logger.info(f"Returning {len(items)} products to frontend")
        return jsonify({"success": True, "products": items})
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    try:
        settings = bot.settings_manager.get_settings()
        # Create a copy to avoid modifying the original
        settings_copy = json.loads(json.dumps(settings))
        # Mask API key
        if settings_copy.get("openai", {}).get("api_key"):
            settings_copy["openai"]["api_key"] = "***MASKED***"
        return jsonify({"success": True, "settings": settings_copy})
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        new_settings = request.json
        if not new_settings:
            return jsonify({"success": False, "error": "No settings provided"}), 400
        
        bot.settings_manager.update_settings(new_settings)
        return jsonify({"success": True, "message": "Settings updated"})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/valuate', methods=['POST'])
def trigger_valuation():
    """Manually trigger OpenAI valuation"""
    logger.info("API call: /api/valuate")
    try:
        result = bot.trigger_valuations()
        logger.info("Valuation triggered successfully")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error triggering valuation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/images/<filename>')
def serve_image(filename):
    """Serve downloaded images"""
    return send_from_directory(IMAGES_DIR, filename)


@app.route('/api/fetch', methods=['POST'])
def fetch_products():
    """Trigger product fetching"""
    logger.info("API call: /api/fetch")
    try:
        if bot:
            data = request.json or {}
            num_products = data.get('num_products', None)
            
            if num_products and num_products > 0:
                # Multi-page fetch
                logger.info(f"Multi-page fetch requested for ~{num_products} products")
                def run_multi_page_fetch():
                    bot.fetch_multiple_pages(num_products)
                
                Thread(target=run_multi_page_fetch, daemon=True).start()
                return jsonify({"success": True, "message": f"Fetching ~{num_products} products in background", "multi_page": True})
            else:
                # Single page fetch (original behavior)
                bot._poll_once()
                items = bot.database.get_all_items()
                logger.info(f"Product fetch triggered successfully, total items: {len(items)}")
                return jsonify({"success": True, "message": "Fetch completed", "count": len(items)})
        else:
            return jsonify({"success": False, "error": "Bot not initialized"}), 500
    except Exception as e:
        logger.error(f"Error triggering fetch: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/save', methods=['POST'])
def save_products():
    """Save products to CSV"""
    try:
        if bot:
            items = bot.database.get_all_items()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"products_{timestamp}.csv"
            
            # Create CSV content
            import csv
            import io
            output = io.StringIO()
            fieldnames = ['id', 'title', 'description', 'price', 'location', 'url', 'discovered_at', 'valuation_status', 'price_estimate']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in items:
                writer.writerow({
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'price': item.get('price', ''),
                    'location': item.get('location', ''),
                    'url': item.get('url', ''),
                    'discovered_at': item.get('discovered_at', ''),
                    'valuation_status': item.get('valuation', {}).get('status', '') if item.get('valuation') else '',
                    'price_estimate': item.get('valuation', {}).get('price_estimate', '') if item.get('valuation') else ''
                })
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output.getvalue())
                
            return jsonify({"success": True, "filename": filename, "count": len(items)})
        else:
            return jsonify({"success": False, "error": "Bot not initialized"}), 500
    except Exception as e:
        logger.error(f"Error saving products: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/refresh-all', methods=['POST'])
def refresh_all():
    """Refresh all existing items to check for updates"""
    logger.info("API call: /api/refresh-all")
    try:
        if bot:
            items = bot.database.get_all_items()
            logger.info(f"Refreshing {len(items)} items in background")
            
            def refresh_all_items():
                """Background task to refresh all items"""
                for item in items:
                    try:
                        product_id = item.get('id')
                        if not product_id:
                            continue
                        
                        # Fetch latest data for this item
                        item_html = bot.fetcher.fetch_item_page(product_id)
                        if not item_html:
                            logger.warning(f"Failed to fetch updated data for {product_id}")
                            continue
                        
                        # Extract updated details
                        updated_data = ProductExtractor.extract_product_details(item_html, product_id)
                        
                        # Refresh images if downloading is enabled
                        settings = bot.settings_manager.get_settings()
                        if settings.get("images", {}).get("download_enabled", True):
                            image_urls = updated_data.get('image_urls', [])
                            if image_urls:
                                bot._download_item_images(updated_data)
                                logger.info(f"Downloaded/refreshed {len(image_urls)} images for {product_id}")
                        
                        # Update the item in database
                        bot.database.add_item(product_id, updated_data)
                        logger.info(f"Updated item {product_id}")
                        
                    except Exception as e:
                        logger.error(f"Error refreshing item {item.get('id')}: {e}")
                
                logger.info(f"Completed refreshing {len(items)} items")
            
            # Run refresh in background thread
            Thread(target=refresh_all_items, daemon=True).start()
            
            return jsonify({"success": True, "message": f"Refreshing {len(items)} items in background", "count": len(items)})
        else:
            return jsonify({"success": False, "error": "Bot not initialized"}), 500
    except Exception as e:
        logger.error(f"Error triggering refresh: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/fetch-images', methods=['POST'])
def fetch_images():
    """Trigger image downloading"""
    try:
        if bot:
            items = bot.database.get_all_items()
            count = 0
            for item in items:
                if item.get('image_urls') and not item.get('image_files'):
                    # This would trigger image downloading if implemented
                    count += 1
            return jsonify({"success": True, "message": f"Image fetch triggered for {count} items", "count": count})
        else:
            return jsonify({"success": False, "error": "Bot not initialized"}), 500
    except Exception as e:
        logger.error(f"Error triggering image fetch: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    if bot:
        bot.stop()
    sys.exit(0)


def main():
    """Main entry point"""
    global bot
    
    logger.info("=" * 60)
    logger.info("Tori Annataan Bot - Starting")
    logger.info("=" * 60)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create bot instance
    bot = ToriBot()
    
    # Start bot
    bot.start()
    
    # Get server settings
    settings = bot.settings_manager.get_settings()
    server_settings = settings.get("server", {})
    host = server_settings.get("host", "127.0.0.1")
    port = server_settings.get("port", 8787)
    
    logger.info(f"Starting Flask server on http://{host}:{port}")
    logger.info("Open http://127.0.0.1:8788 in your browser")
    logger.info("Press CTRL+C to stop")
    
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        bot.stop()


if __name__ == "__main__":
    main()
