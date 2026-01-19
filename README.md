# ToriBot

Tori.fi bot ilmaisten tuotteiden arvottamista varten - A bot for monitoring new products on Tori.fi

## Features

- 🔄 Automatically polls Tori.fi every 60 seconds for new products
- 🔍 Extracts product details (title, description, location, seller, images)
- 💾 Stores products in JSON format with duplicate prevention
- 🌐 Web-based GUI with auto-refresh
- 📊 Clean, responsive table view of all monitored products

## Files

- **toribot.py** - Main bot script with polling logic and HTTP server
- **gui.html** - Web interface for viewing products
- **styles.css** - Styling for the web interface
- **products.json** - Product data storage (created automatically)

## Requirements

- Python 3.6+
- No external dependencies (uses only Python standard library)

## Usage

1. **Start the bot:**
   ```bash
   python3 toribot.py
   ```

2. **Open the GUI in your browser:**
   ```
   http://localhost:8000/gui.html
   ```

3. **The bot will:**
   - Poll https://www.tori.fi/recommerce/forsale/search?sort=PUBLISHED_DESC&trade_type=2 every 60 seconds
   - Extract new product IDs using regex pattern `/recommerce/forsale/item/<id>`
   - Fetch detailed information for each new product
   - Save data to `products.json` (duplicates are automatically prevented)
   - Serve the GUI on port 8000

4. **The GUI will:**
   - Display all products in a responsive table
   - Auto-refresh every 30 seconds
   - Show product images, titles, descriptions, locations, sellers, and timestamps
   - Provide links to view products on Tori.fi

## Architecture

The code is designed to be clean and extendable:

- **ProductStorage**: Handles all JSON file operations and duplicate checking
- **ToriFetcher**: Manages HTTP requests and HTML parsing with regex
- **ToriBot**: Coordinates polling and integrates storage with fetcher
- **HTTP Server**: Serves static files for the web GUI

## Configuration

Edit these constants in `toribot.py` to customize:

```python
SEARCH_URL = "..."      # The Tori.fi search URL to monitor
POLL_INTERVAL = 60      # Polling interval in seconds
SERVER_PORT = 8000      # HTTP server port
PRODUCTS_FILE = "..."   # Products JSON file path
```

## Stopping the Bot

Press `Ctrl+C` to gracefully shut down the bot.
