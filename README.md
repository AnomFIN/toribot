# Tori Bots 🎁💰

Complete working bots for monitoring Tori.fi listings with OpenAI-based valuation.

## Two Bots Available

### 1. Tori Annataan Bot 🎁
Monitors **free items** ("Annataan" = Given away for free)
- Port: 8788
- Run with: `python3 toribot.py`
- See: http://127.0.0.1:8788

### 2. Tori Ostobotti 💰
Monitors **wanted/buying requests** ("Ostetaan" = Wanted to buy)
- Port: 8789
- Run with: `python3 ostobotti.py`
- See: http://127.0.0.1:8789
- Full documentation: [OSTOBOTTI_README.md](OSTOBOTTI_README.md)

Both bots can run simultaneously without conflicts!

## Features

- 🔄 **Automatic Polling**: Checks Tori.fi periodically (configurable)
- 🖼️ **Image Download**: Downloads up to 5 images per item
- 🤖 **OpenAI Valuation**: Automatic item valuation using GPT models
- ⚙️ **Web GUI**: Modern interface with settings management
- 💾 **Persistent Storage**: All state stored in JSON files
- 🛡️ **Robust Error Handling**: Never crashes, tracks errors per item
- 🌐 **Polite Crawling**: Jitter, retries, and exponential backoff

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Bot(s)

For **free items** bot:
```bash
python3 toribot.py
```

For **wanted/buying** bot:
```bash
python3 ostobotti.py
```

You can run both simultaneously!

### 3. Open GUI

- Annataan Bot (free items): http://127.0.0.1:8788
- Ostobotti (buying requests): http://127.0.0.1:8789

## File Structure

```
/toribot/
  # Annataan Bot (Free Items)
  toribot.py            # Main bot application
  gui.html              # Web interface
  products.json         # Product database (auto-created)
  settings.json         # Settings (auto-created)
  /debug/               # Debug logs (auto-created)
  /images/              # Downloaded images (auto-created)
  
  # Ostobotti (Wanted/Buying)
  ostobotti.py          # Ostobotti application
  ostobotti_gui.html    # Web interface
  ostobotti_products.json  # Product database (auto-created)
  ostobotti_settings.json  # Settings (auto-created)
  /ostobotti_debug/     # Debug logs (auto-created)
  /ostobotti_images/    # Downloaded images (auto-created)
  
  # Shared
  styles.css            # Styling (shared)
  requirements.txt      # Python dependencies (shared)
  OSTOBOTTI_README.md   # Ostobotti documentation
```

## Settings

All settings can be managed via the GUI:

### General
- **Poll Interval**: How often to check for new items (default: 60s)
- **Request Timeout**: HTTP request timeout (default: 15s)
- **Max Retries**: Number of retry attempts (default: 2)

### Images
- **Download Enabled**: Toggle image downloading
- **Max Images**: Number of images per item (default: 5)

### OpenAI
- **API Key**: Your OpenAI API key (stored securely in settings.json)
- **Model**: Model to use (default: gpt-4o-mini)
- **Valuation Interval**: How often to run valuations (default: 60 min)

### Server
- **Host**: Server host (default: 127.0.0.1)
- **Port**: Server port (default: 8787)

## Usage

### Products Tab
- View all discovered items
- See images, descriptions, locations, sellers
- Read OpenAI valuations
- Click "View" to open item on Tori.fi
- Click "Run Valuations" to manually trigger OpenAI analysis

### Settings Tab
- Modify all bot settings
- Save OpenAI API key
- Changes take effect immediately (except server settings)

## Safety Features

- **Graceful Shutdown**: Press CTRL+C to stop cleanly
- **Error Tracking**: Each item tracks extraction errors
- **Retry Logic**: Exponential backoff for failed requests
- **Jitter**: Random 0-3s delay to avoid pattern detection
- **State Persistence**: All data saved to JSON files
- **No Crashes**: Comprehensive exception handling

## Architecture

```python
# Clean separation of concerns
SettingsManager      # Settings persistence and validation
ProductDatabase      # Product storage with thread-safe operations
ToriFetcher          # HTTP requests with retries and jitter
ProductExtractor     # HTML parsing and data extraction
OpenAIValuator       # OpenAI API integration
ToriBot              # Main coordinator with background threads
Flask App            # REST API and GUI serving
```

## API Endpoints

- `GET /` - Serve GUI
- `GET /api/products` - Get all products
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings
- `POST /api/valuate` - Trigger manual valuation
- `GET /images/<filename>` - Serve downloaded images

## Requirements

- Python 3.8+
- flask >= 3.0.0
- flask-cors >= 4.0.0
- requests >= 2.31.0
- pillow >= 10.0.0
- openai >= 1.0.0

## License

Personal use project for monitoring Tori.fi listings.
