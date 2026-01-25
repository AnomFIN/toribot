#!/usr/bin/env python3
"""
Toribot Base Module - Shared code for Tori.fi monitoring bots
Contains all common classes and functions used by both toribot.py and ostobotti.py
"""

import re
import json
import time
import logging
import os
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
    import sys
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Regex pattern
PRODUCT_ID_PATTERN = r'href=["\'][^"\']*?/recommerce/forsale/item/(\d+)'


class SettingsManager:
    """Manages application settings with file persistence"""
    
    def __init__(self, filename, default_settings):
        self.filename = filename
        self.default_settings = default_settings
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
                return self.default_settings.copy()
        else:
            logger.info("Settings file not found. Creating with defaults.")
            self._save_settings(self.default_settings)
            return self.default_settings.copy()
    
    def _merge_with_defaults(self, loaded):
        """Merge loaded settings with defaults to handle missing keys"""
        # Use deep copy to avoid mutating default_settings
        result = copy.deepcopy(self.default_settings)
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
    
    def __init__(self, filename):
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
            # First get login page for any tokens/csrf (unused variable fixed)
            self.session.get("https://www.tori.fi/")
            
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
            # NOTE: In ostobotti context, this refers to the buyer/requester who posted the "wanted" listing
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
            
            # Images - improved extraction with strict validation
            images = []
            image_patterns = [
                # Primary product image patterns (high priority)
                r'"mainImage"\s*:\s*"(https://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
                r'"imageUrl"\s*:\s*"(https://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
                r'"productImage"\s*:\s*"(https://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
                
                # Gallery patterns (medium priority)
                r'data-src="(https://[^"]*(?:images|img)[^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"',
                r'src="(https://[^"]*(?:images|img)[^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"',
                
                # Fallback patterns (low priority)
                r'"image"\s*:\s*"(https://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
            ]
            
            # Filter patterns to avoid ads and UI elements
            ad_patterns = [
                r'banner', r'advertisement', r'promo', r'logo', r'icon',
                r'avatar', r'thumbnail', r'watermark', r'overlay'
            ]
            
            for pattern in image_patterns:
                img_matches = re.findall(pattern, html, re.IGNORECASE)
                for match in img_matches:
                    img_url = match if isinstance(match, str) else match[0]
                    
                    # Validate image URL
                    if (img_url and 
                        img_url.startswith('https://') and
                        # Ensure it's from a trusted domain
                        ('tori.fi' in img_url or 'tor.se' in img_url or 'images' in img_url) and
                        # Avoid ad/UI images
                        not any(ad_term in img_url.lower() for ad_term in ad_patterns) and
                        # Must have proper image extension
                        re.search(r'\.(jpg|jpeg|png|webp)(\?|$)', img_url, re.IGNORECASE)):
                        
                        images.append(img_url)
            
            # Remove duplicates while preserving order, limit to 5
            seen = set()
            unique_images = []
            for img in images:
                if img not in seen and len(unique_images) < 5:
                    seen.add(img)
                    unique_images.append(img)
            images = unique_images
            
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
    
    def __init__(self, settings_manager, valuation_prompt_builder):
        self.settings_manager = settings_manager
        self.valuation_prompt_builder = valuation_prompt_builder
    
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
            
            # Get prompt from configuration
            system_message, user_prompt = self.valuation_prompt_builder(item)
            
            # Call API
            response = client.chat.completions.create(
                model=openai_settings.get("model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
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
    
    def __init__(self, config):
        """
        Initialize bot with configuration
        
        Args:
            config: Dictionary with keys:
                - settings_file: path to settings file
                - products_file: path to products file
                - debug_dir: path to debug directory
                - images_dir: path to images directory
                - default_settings: default settings dict
                - valuation_prompt_builder: function(item) -> (system_message, user_prompt)
                    that builds OpenAI prompts for the specific bot type
        """
        self.config = config
        self.settings_manager = SettingsManager(
            config['settings_file'],
            config['default_settings']
        )
        self.database = ProductDatabase(config['products_file'])
        self.fetcher = ToriFetcher(self.settings_manager)
        self.valuator = OpenAIValuator(
            self.settings_manager,
            config['valuation_prompt_builder']
        )
        
        self.running = False
        self.stop_event = Event()
        self.poll_thread = None
        self.valuation_thread = None
        self.last_valuation_time = None
        
        # Ensure directories exist
        Path(config['debug_dir']).mkdir(exist_ok=True)
        Path(config['images_dir']).mkdir(exist_ok=True)
        
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
                filepath = os.path.join(self.config['images_dir'], filename)
                
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
        """Fetch products from multiple pages based on requested count"""
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
