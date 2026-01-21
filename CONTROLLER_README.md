# Toribot Controller & Unified GUI

## Overview

Two new management interfaces have been added to control and monitor both Toribot (Annataan) and Ostobotti (Ostetaan):

1. **TUI Controller** (`toribot_controller.py`) - Terminal-based interface
2. **Unified GUI** (`unified_gui.html`) - Web-based interface

## 1. TUI Controller (Terminal Interface)

### Features

- Start/stop individual bots (only one running at a time)
- View real-time logs
- Check bot status
- Open web GUI from terminal
- Color-coded terminal output

### Usage

```bash
# Navigate to toribot directory
cd /path/to/toribot

# Run the controller
python3 toribot_controller.py
```

### Menu Options

```
1. Start Toribot (Free Items - Annataan)
2. Start Ostobotti (Wanted/Buying - Ostetaan)
3. Stop Running Bot
4. View Logs (Last 20 lines)
5. View Status
6. Open Web GUI
0. Exit
```

### Features Detail

**Start Bot:** Launches selected bot in background process
- Only one bot can run at a time
- Automatic port detection (8788 for Toribot, 8789 for Ostobotti)
- Startup verification with error handling

**Stop Bot:** Gracefully stops running bot
- Sends SIGINT for clean shutdown
- Falls back to force kill if needed (10s timeout)
- Cleans up process resources

**View Logs:** Shows recent log output
- Last 20 lines by default
- Real-time buffer of last 100 lines
- Color-coded for easy reading

**View Status:** Displays detailed information
- Active bot name and PID
- Bot type and port
- Data file status and sizes
- Last modification times

**Open GUI:** Launches web browser
- Automatically opens correct port
- Falls back to URL display if browser fails

### Requirements

- Python 3.6+
- Both `toribot.py` and `ostobotti.py` must be in same directory
- Standard library only (no additional dependencies)

---

## 2. Unified GUI (Web Interface)

### Features

- View data from **both bots simultaneously**
- Toggle between bots with animated slider
- Real-time connection status
- Unified statistics dashboard
- Direct links to individual bot GUIs

### Usage

#### Option A: Direct File Access
Simply open `unified_gui.html` in your web browser:
```bash
# Linux/Mac
open unified_gui.html

# Or
firefox unified_gui.html
google-chrome unified_gui.html
```

#### Option B: Serve via Python HTTP Server
```bash
python3 -m http.server 8080
# Then open http://localhost:8080/unified_gui.html
```

#### Option C: Access from TUI Controller
1. Start one or both bots via TUI controller
2. The unified GUI will automatically detect which bots are running

### Interface Components

**Connection Status Cards:**
- Shows online/offline status for each bot
- Animated pulse indicator for online bots
- Port information

**Bot Switcher:**
- Animated toggle slider (🎁 ↔ 💰)
- Switch between Annataan and Ostetaan views
- Visual feedback for active selection

**Products Display:**
- Grid view of up to 20 most recent products
- Product images with fallback
- Description preview
- Location and valuation info
- Direct links to Tori.fi listings

**Statistics Dashboard:**
- Total products count
- New today count
- Products with AI valuation

**Action Buttons:**
- Refresh: Update product data
- Open Bot GUI: Launch bot-specific interface

### Technical Details

**API Integration:**
- Connects to both bot APIs simultaneously:
  - Toribot: `http://127.0.0.1:8788/api`
  - Ostobotti: `http://127.0.0.1:8789/api`

**Auto-refresh:**
- Status check and data refresh every 2 minutes
- Manual refresh available via button

**Cross-Origin:**
- Works with file:// protocol
- No CORS issues (same-origin APIs)

---

## Comparison: TUI vs Unified GUI

| Feature | TUI Controller | Unified GUI |
|---------|---------------|-------------|
| Bot Management | ✅ Start/Stop | ❌ View only |
| Single Instance | ✅ Enforced | N/A |
| Both Bots View | ❌ One at a time | ✅ Toggle view |
| Logs Access | ✅ Real-time | ❌ |
| Web Interface | Via option 6 | Native |
| Requirements | Python only | Modern browser |
| Remote Access | SSH/Terminal | HTTP server |

---

## Recommended Workflow

### Local Development/Testing
1. Use **TUI Controller** for bot lifecycle management
2. Use **Unified GUI** for monitoring and data browsing

### Production/Server
1. Use **TUI Controller** or systemd/supervisor for process management
2. Access **Unified GUI** via web server for monitoring

### Quick Demo
```bash
# Terminal 1: Start controller
python3 toribot_controller.py
# Choose option 1 or 2 to start a bot

# Terminal 2: Open unified GUI
firefox unified_gui.html
# Or use option 6 from TUI controller
```

---

## Screenshots

### TUI Controller
```
============================================================
        🤖 TORIBOT CONTROLLER 🤖
============================================================
Status: RUNNING | Active Bot: Toribot
============================================================

Main Menu:
  1. Start Toribot (Free Items - Annataan)
  2. Start Ostobotti (Wanted/Buying - Ostetaan)
  3. Stop Running Bot
  4. View Logs (Last 20 lines)
  5. View Status
  6. Open Web GUI
  0. Exit

Enter your choice:
```

### Unified GUI
- Header: "🤖 Toribot Unified Dashboard"
- Status cards showing online/offline for both bots
- Toggle slider: 🎁 ↔ 💰
- Product grid with images and details
- Statistics dashboard

---

## Troubleshooting

### TUI Controller Issues

**"Bot files not found"**
- Ensure you're in the correct directory
- Both `toribot.py` and `ostobotti.py` must exist

**Bot won't start**
- Check if port is already in use
- Verify Python dependencies are installed
- Check file permissions

**Can't stop bot**
- Try option 3 again (force kill after 10s)
- Manually find PID: `ps aux | grep toribot`
- Kill manually: `kill -9 <PID>`

### Unified GUI Issues

**"Checking..." status stuck**
- Ensure at least one bot is running
- Check browser console for errors
- Verify API endpoints are accessible

**No products shown**
- Bots need time to fetch initial data
- Click "Refresh" button
- Check individual bot GUIs

**Images not loading**
- Images load from bot directories
- Ensure image download is enabled in bot settings
- Check browser security settings for local files

---

## Future Enhancements

Potential improvements:
- [ ] WebSocket support for real-time updates
- [ ] Combined search across both bots
- [ ] Export merged data to CSV
- [ ] Side-by-side comparison view
- [ ] Bot configuration editor
- [ ] Scheduled start/stop times
- [ ] Email/notification alerts

---

## License

Same as main Toribot project.
