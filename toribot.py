#!/usr/bin/env python3
"""
Tori Annataan Bot - Free items monitoring bot
Goal: Poll Tori.fi "annataan" (free) listings, detect new items, download images,
      run OpenAI valuations, and provide modern GUI with settings management.
"""

import signal
import sys
import json
import csv
from io import StringIO
from datetime import datetime
from threading import Thread

# Import shared base module
from toribot_base import (
    Flask, jsonify, request, send_from_directory,
    logger, ToriBot, ProductExtractor
)

# Configuration for Annataan Bot
PRODUCTS_FILE = "products.json"
SETTINGS_FILE = "settings.json"
DEBUG_DIR = "debug"
IMAGES_DIR = "images"
GUI_FILE = "gui.html"

# Default settings for Annataan Bot
DEFAULT_SETTINGS = {
    "poll_interval_seconds": 60,
    "listing_url": "https://www.tori.fi/recommerce/forsale/search?sort=PUBLISHED_DESC&trade_type=2",
    "request_timeout_seconds": 15,
    "max_retries": 2,
    "products_per_page": 50,
    "openai": {
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "valuation_interval_minutes": 60,
        "enabled": True
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


def build_annataan_valuation_prompt(item):
    """Build OpenAI prompts for free items (Annataan)
    
    Args:
        item: Dictionary containing item data (title, description, location, seller)
        
    Returns:
        tuple: (system_message, user_prompt) for OpenAI API
    """
    system_message = "Olet hyödyllinen avustaja joka arvioi ilmaisia tuotteita suomeksi. Anna realistisia hinta-arvioita euroina."
    
    user_prompt = f"""Analysoi tämä ilmainen tuote Tori.fi palvelusta ja anna lyhyt arvio suomeksi:

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
    
    return system_message, user_prompt


# Flask Application
app = Flask(__name__)

# Global bot instance
bot = None


@app.route('/')
def index():
    """Serve main GUI"""
    return send_from_directory('.', GUI_FILE)


@app.route('/gui.html')
def gui():
    """Serve GUI HTML file"""
    return send_from_directory('.', GUI_FILE)


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
        # Mask API key
        settings_copy = json.loads(json.dumps(settings))
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


@app.route('/v2')
@app.route('/v2/')
def v2_index():
    """Serve v2 GUI"""
    return send_from_directory('static/v2', 'index.html')


@app.route('/static/v2/<path:path>')
def serve_v2_static(path):
    """Serve v2 static files"""
    return send_from_directory('static/v2', path)


@app.route('/api/health')
def get_health():
    """Get bot health status"""
    try:
        items = bot.database.get_all_items()
        settings = bot.settings_manager.get_settings()
        
        # Compute the latest discovered_at timestamp explicitly, since item order is not guaranteed
        last_update = max(
            (item.get("discovered_at") for item in items if item.get("discovered_at") is not None),
            default=None,
        )

        return jsonify({
            "success": True,
            "status": "running",
            "version": "2.0.0",
            "products_count": len(items),
            "openai_enabled": settings.get("openai", {}).get("enabled", False),
            "last_update": last_update
        })
    except Exception as e:
        logger.error(f"Error getting health: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


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
            output = StringIO()
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
                            image_urls = updated_data.get('images', [])
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
    
    # Create bot configuration
    bot_config = {
        'settings_file': SETTINGS_FILE,
        'products_file': PRODUCTS_FILE,
        'debug_dir': DEBUG_DIR,
        'images_dir': IMAGES_DIR,
        'default_settings': DEFAULT_SETTINGS,
        'valuation_prompt_builder': build_annataan_valuation_prompt
    }
    
    # Create bot instance
    bot = ToriBot(bot_config)
    
    # Start bot
    bot.start()
    
    # Get server settings
    settings = bot.settings_manager.get_settings()
    server_settings = settings.get("server", {})
    host = server_settings.get("host", "127.0.0.1")
    port = server_settings.get("port", 8788)
    
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
