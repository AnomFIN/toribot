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
from datetime import datetime
from threading import Thread, Event, Lock
from pathlib import Path
from html import unescape

# Third-party imports
try:
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
    import requests
    from PIL import Image
    from io import BytesIO
except ImportError as e:
    print(f"Error: Missing required package. Install with: pip install flask flask-cors requests pillow openai")
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
        "port": 8787
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
        result = DEFAULT_SETTINGS.copy()
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
    
    def fetch_listing_page(self):
        """Fetch main listing page"""
        settings = self.settings_manager.get_settings()
        url = settings.get("listing_url")
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
            
            # Location
            location = None
            match = re.search(r'"location"\s*:\s*"([^"]+)"', html, re.IGNORECASE)
            if match:
                location = ProductExtractor._clean_text(match.group(1))
            else:
                errors.append("Failed to extract location")
            
            # Seller
            seller = None
            match = re.search(r'"seller"[^}]*"name"\s*:\s*"([^"]+)"', html, re.IGNORECASE)
            if match:
                seller = ProductExtractor._clean_text(match.group(1))
            else:
                errors.append("Failed to extract seller")
            
            # Images
            images = []
            img_pattern = r'"image"\s*:\s*"(https://[^"]+)"'
            img_matches = re.findall(img_pattern, html, re.IGNORECASE)
            images = list(set(img_matches))[:5]  # Max 5 unique images
            
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
            prompt = f"""Analyze this free item listing from Tori.fi and provide a brief valuation:

Title: {item.get('title', 'N/A')}
Description: {item.get('description', 'N/A')}
Location: {item.get('location', 'N/A')}

Provide:
1. Estimated market value (if sold)
2. Condition assessment
3. Key pros/cons
4. Worth picking up? (Yes/No/Maybe)

Be concise (max 100 words)."""
            
            # Call API
            response = client.chat.completions.create(
                model=openai_settings.get("model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that evaluates free items."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            valuation_text = response.choices[0].message.content.strip()
            
            return {
                "status": "completed",
                "text": valuation_text,
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
    
    def _poll_once(self):
        """Perform one polling cycle"""
        logger.info("Polling for new items...")
        
        # Fetch listing page
        html = self.fetcher.fetch_listing_page()
        if not html:
            logger.warning("Failed to fetch listing page")
            return
        
        # Extract product IDs
        product_ids = ProductExtractor.extract_product_ids(html)
        logger.info(f"Found {len(product_ids)} product IDs")
        
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
            logger.info(f"Added {new_count} new items")
        else:
            logger.info("No new items found")
    
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


# Flask Application
app = Flask(__name__)
CORS(app)

# Global bot instance
bot = None


@app.route('/')
def index():
    """Serve main GUI"""
    return send_from_directory('.', 'gui.html')


@app.route('/styles.css')
def styles():
    """Serve CSS"""
    return send_from_directory('.', 'styles.css')


@app.route('/api/products')
def get_products():
    """Get all products"""
    try:
        items = bot.database.get_all_items()
        # Sort by discovered_at descending
        items.sort(key=lambda x: x.get('discovered_at', ''), reverse=True)
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
    try:
        result = bot.trigger_valuations()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error triggering valuation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/images/<filename>')
def serve_image(filename):
    """Serve downloaded images"""
    return send_from_directory(IMAGES_DIR, filename)


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
    logger.info("Open http://127.0.0.1:8787 in your browser")
    logger.info("Press CTRL+C to stop")
    
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        bot.stop()


if __name__ == "__main__":
    main()
