# ToriBot v2 Dashboard - User Guide

## Overview

ToriBot v2 is a complete redesign of the dashboard interface, providing a modern, professional, and user-friendly experience for monitoring Tori.fi listings. Built with vanilla JavaScript and modern CSS, it offers enhanced functionality while maintaining full backward compatibility with v1.

## Screenshots

### Dark Theme
![Dashboard Dark](https://github.com/user-attachments/assets/23992ab9-71b9-4555-bfb6-cb759e85fc29)
*Main dashboard with stats cards and quick actions*

### Light Theme
![Dashboard Light](https://github.com/user-attachments/assets/44cb7d9f-5709-4b52-8eb7-7350a90b900f)
*Light theme option for better visibility in bright environments*

### Products Page
![Products](https://github.com/user-attachments/assets/798aba7e-04ed-4bad-a8ca-47fdf7813c38)
*Advanced filtering and view options for products*

### Settings Page
![Settings](https://github.com/user-attachments/assets/e5a96893-9751-4dd6-b982-0668e11081a1)
*Comprehensive settings management interface*

## Getting Started

### Accessing v2 Dashboard

Once your bot is running, access the v2 dashboard at:

**Toribot (free items):**
```
http://127.0.0.1:8788/v2
```

**Ostobotti (wanted/buying):**
```
http://127.0.0.1:8789/v2
```

**v1 Dashboard (original):**
Both versions remain available. Access v1 at the root URL (`/` instead of `/v2`).

### First Time Setup

1. **Start the bot:**
   ```bash
   python3 toribot.py
   # or
   python3 ostobotti.py
   ```

2. **Open your browser** and navigate to the v2 URL

3. **Configure settings** (Settings page):
   - Set poll interval
   - Enable image downloads
   - Configure OpenAI API key (optional)

4. **Fetch products** (Dashboard):
   - Click "Fetch New Products" button
   - Wait for products to load
   - Products will appear in the dashboard

## Features Guide

### 🏠 Dashboard

The main overview of your bot's activity.

**Components:**
- **Stats Cards**: Quick view of key metrics
  - Total Products: Number of products discovered
  - New Today: Products found today
  - AI Valuated: Products with OpenAI analysis
  - Errors: Products with extraction issues

- **Quick Actions**: One-click operations
  - Fetch New Products: Poll Tori.fi for new listings
  - Run AI Valuation: Trigger OpenAI analysis
  - Refresh All Products: Update existing product data
  - Export to CSV: Save products to CSV file

- **Recent Products**: Grid view of latest 6 products
  - Click any product to view full details
  - Shows images, title, description, location
  - Badge indicates AI valuation status

**Product Detail Modal:**
- Full-size product images
- Complete description
- Location and seller information
- AI valuation (if available)
- Direct link to Tori.fi listing

### 📦 Products

Browse and manage all discovered products.

**Filters:**
- **Search**: Filter by title or description
- **Location**: Filter by location name
- **Date From**: Show products after specific date
- **Has Valuation**: Filter by AI valuation status

**View Modes:**
- **Grid View**: Card-based layout with images
- **Table View**: Compact table with more information

**Features:**
- Pagination for large datasets
- Sort options (coming soon)
- Bulk actions (coming soon)
- Export filtered results (coming soon)

**Actions per Product:**
- View details (eye icon)
- Open on Tori.fi (external link icon)

### 📝 Logs

View bot activity logs.

**Features:**
- Log level filtering (All, Info, Warning, Error)
- Auto-scroll toggle
- Copy logs to clipboard
- Clear logs option

**Note:** Real-time log streaming from debug files is planned for a future update. Currently shows simulated logs based on bot status.

### ⚙️ Settings

Configure bot behavior.

**General Settings:**
- **Poll Interval**: How often to check Tori.fi (seconds)
- **Request Timeout**: HTTP request timeout (seconds)
- **Max Retries**: Number of retry attempts
- **Products Per Page**: Items to fetch per request

**Image Settings:**
- **Enable Image Download**: Toggle image downloading
- **Max Images Per Item**: Number of images to download (1-10)

**OpenAI Settings:**
- **Enable OpenAI Valuation**: Toggle AI analysis
- **Valuation Interval**: How often to run analysis (minutes)
- **API Key**: Your OpenAI API key
- **Model**: GPT model to use (gpt-4o-mini, gpt-4o, etc.)
- **Base URL**: OpenAI API endpoint

**Server Settings:**
- **Host**: Server bind address
- **Port**: Server port number
- ⚠️ **Note**: Changes require bot restart

**Actions:**
- **Reset**: Restore form to saved values
- **Save Settings**: Apply and save changes

## User Interface Elements

### Navigation

**Sidebar:**
- Collapsible sidebar (click hamburger icon)
- Active page highlighted
- Logo and branding
- Theme toggle at bottom

**Header:**
- Page title
- Global search (searches products)
- Bot status indicator
  - 🟢 Green = Online
  - 🔴 Red = Offline

### Components

**Buttons:**
- Primary: Main actions (blue)
- Secondary: Alternative actions (gray)
- Danger: Destructive actions (red)

**Cards:**
- Hover effects show interactivity
- Clean borders and shadows

**Badges:**
- Color-coded status indicators
- Success (green), Error (red), Warning (yellow), Info (blue)

**Modals:**
- Click outside or X to close
- Press Escape to close

**Toast Notifications:**
- Auto-dismiss after 4-6 seconds
- Click X to close immediately
- Shows in top-right corner

## Keyboard Shortcuts

Currently not implemented. Planned for future release.

## Theme System

### Dark Theme (Default)
- Deep blue-gray backgrounds
- Purple/blue accents
- Optimized for low-light environments
- Easy on the eyes for extended use

### Light Theme
- Clean white/gray backgrounds
- Same accent colors
- Better visibility in bright environments
- High contrast for accessibility

**Toggle Theme:**
- Click "Dark Mode" or "Light Mode" button in sidebar
- Theme preference saved automatically
- Applies instantly without page reload

## Mobile Experience

The v2 dashboard is fully responsive and works on mobile devices:

**Mobile Optimizations:**
- Hamburger menu for navigation
- Touch-optimized controls
- Responsive grid layouts
- Optimized for portrait and landscape
- Large tap targets for buttons

**Navigation:**
- Tap hamburger icon to open sidebar
- Tap outside sidebar to close
- All features accessible on mobile

## Tips & Best Practices

### Performance
- Use pagination for large product lists
- Enable image downloading only if needed
- Adjust poll interval based on activity

### OpenAI Usage
- Set appropriate valuation interval to control costs
- Use gpt-4o-mini for cost-effective analysis
- Monitor usage in OpenAI dashboard

### Data Management
- Export products regularly to CSV
- Clear old products periodically (via v1 or database)
- Monitor errors in stats cards

### Troubleshooting
- Check bot status indicator in header
- Review error messages in toast notifications
- Check settings if bot not fetching products
- Restart bot after server settings changes

## Technical Details

### Browser Compatibility
- Chrome/Edge: ✅ Fully supported
- Firefox: ✅ Fully supported
- Safari: ✅ Fully supported
- Mobile browsers: ✅ Fully supported

### Requirements
- Modern browser (ES6+ support)
- JavaScript enabled
- Running bot instance

### Architecture
```
/static/v2/
├── index.html              # Main HTML file
├── app.js                  # Core application
├── config.json             # Configuration
├── styles/
│   ├── theme.css          # Theme system
│   ├── components.css     # UI components
│   └── layout.css         # Layout system
├── services/
│   ├── api.js             # API client
│   ├── state.js           # State management
│   ├── toast.js           # Notifications
│   └── ui.js              # UI utilities
└── features/
    ├── dashboard.js       # Dashboard page
    ├── products.js        # Products page
    ├── logs.js            # Logs page
    └── settings.js        # Settings page
```

### API Endpoints Used
- `GET /api/products` - Get all products
- `GET /api/settings` - Get bot settings
- `POST /api/settings` - Update settings
- `POST /api/valuate` - Trigger AI valuation
- `POST /api/fetch` - Fetch new products
- `POST /api/save` - Export to CSV
- `POST /api/refresh-all` - Refresh all products
- `GET /api/health` - Bot health check
- `GET /images/*` - Serve product images

## Comparison: v1 vs v2

| Feature | v1 | v2 |
|---------|----|----|
| UI Design | Basic | Modern |
| Dark/Light Theme | ❌ | ✅ |
| Mobile Responsive | Limited | Full |
| Advanced Filters | Basic | Advanced |
| Pagination | ❌ | ✅ |
| Toast Notifications | ❌ | ✅ |
| Loading States | Basic | Skeleton loaders |
| Empty States | Basic | Enhanced with CTA |
| Product Detail Modal | ❌ | ✅ |
| Grid/Table Toggle | ❌ | ✅ |
| Real-time Status | Basic | Enhanced |
| Settings UI | Functional | Professional |

## Future Enhancements

Planned features for future releases:

- [ ] Real-time log streaming via WebSocket
- [ ] Advanced charts and graphs
- [ ] Authentication system (PIN/token)
- [ ] Keyboard shortcuts
- [ ] Bulk operations on products
- [ ] Custom dashboard layouts
- [ ] Export filtered data
- [ ] Advanced search with regex
- [ ] Product comparison tool
- [ ] Notification preferences
- [ ] Mobile app version

## Getting Help

### Issues
If you encounter problems:
1. Check the browser console (F12) for errors
2. Verify bot is running (check status indicator)
3. Try refreshing the page
4. Clear browser cache
5. Check README and documentation

### Feature Requests
For feature requests or suggestions:
1. Open an issue on GitHub
2. Describe the feature
3. Explain the use case
4. Provide mockups if possible

## Credits

Built with love using:
- Vanilla JavaScript (ES6+)
- CSS Grid & Flexbox
- CSS Custom Properties
- Font Awesome icons
- No frameworks or libraries required!

---

## Quick Reference

**URLs:**
- v2 Dashboard: `http://127.0.0.1:8788/v2` (or 8789 for ostobotti)
- v1 Dashboard: `http://127.0.0.1:8788/` (or 8789 for ostobotti)

**Key Features:**
- 🎨 Dark/Light themes
- 📱 Mobile responsive
- 🔔 Toast notifications
- 📊 Stats dashboard
- 🔍 Advanced filters
- ⚙️ Settings management

**Navigation:**
- Dashboard: Overview and quick actions
- Products: Browse and filter products
- Logs: View bot activity
- Settings: Configure bot behavior

Enjoy the new v2 dashboard! 🎉
