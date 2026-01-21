# ToriBot v2 - Changelog

## Version 2.0.0 - 2026-01-22

### 🎉 Major Release: Complete GUI Overhaul

This release introduces a completely redesigned, modern dashboard interface (v2) while maintaining full backward compatibility with the original v1 GUI.

### ✨ New Features

#### Modern Dashboard Interface
- **Professional Design**: Clean, modern UI with dark/light theme support
- **Component-Based Architecture**: Modular, reusable components for maintainability
- **Responsive Layout**: Fully responsive design that works on desktop, tablet, and mobile
- **Real-Time Updates**: Automatic polling for live status and product updates
- **Enhanced Navigation**: Collapsible sidebar with smooth animations
- **Mobile-Friendly**: Hamburger menu and touch-optimized controls for mobile devices

#### Core Components
- **Stat Cards**: Beautiful animated cards showing key metrics
- **Product Grid/Table**: Toggle between grid and table view for products
- **Advanced Filters**: Search, location, date, and valuation filters
- **Pagination**: Navigate through large product lists efficiently
- **Toast Notifications**: User-friendly notifications for all actions
- **Modal System**: Clean modal dialogs for detailed views
- **Loading States**: Skeleton loaders for better perceived performance
- **Empty States**: Helpful empty state messages with call-to-action buttons
- **Error States**: Clear error messages with retry functionality

#### Features by Page

**Dashboard**
- KPI cards: Total Products, New Today, AI Valuated, Errors
- Quick action buttons for common tasks
- Recent products grid with images
- Product detail modal with full information
- Direct links to Tori.fi listings

**Products**
- Advanced filtering (search, location, date, valuation status)
- Grid/Table view toggle
- Pagination for large datasets
- Product images with fallback
- Status badges for AI valuation
- Sort and filter controls

**Logs**
- Log viewer with syntax highlighting
- Log level filtering (All, Info, Warning, Error)
- Auto-scroll toggle
- Copy to clipboard functionality
- Clear logs option
- Real-time log streaming (backend implementation ready)

**Settings**
- Comprehensive settings management
- General settings (poll interval, timeout, retries)
- Image settings (enable/disable, max images)
- OpenAI settings (API key, model, interval)
- Server settings (host, port)
- Form validation and reset functionality
- Warning badges for settings requiring restart

#### Theme System
- **Dark Theme**: Modern dark blue-gray palette (default)
- **Light Theme**: Clean light gray palette
- **Theme Toggle**: Instant theme switching
- **Persistent Preference**: Theme saved to localStorage
- **Smooth Transitions**: Animated theme switching

#### Technical Improvements
- **State Management**: Reactive state system with subscriptions
- **API Client**: Robust fetch wrapper with error handling and timeouts
- **UI Utilities**: Helper functions for formatting, dates, and common operations
- **Toast Service**: Centralized notification system
- **LocalStorage**: Persistent user preferences
- **TypeScript-Ready**: Structured for easy TypeScript migration

#### New API Endpoints
- `GET /api/health` - Bot health status and metrics
- `GET /v2` - Serve v2 GUI
- `GET /static/v2/*` - Serve v2 static assets

### 🔄 Backward Compatibility

- **v1 GUI Preserved**: Original GUI remains available at root URL (`/`)
- **No Breaking Changes**: All existing API endpoints unchanged
- **Parallel Operation**: v1 and v2 can be used simultaneously
- **Easy Migration**: Switch between v1 and v2 by URL path

### 📊 Statistics

- **16 New Files**: Complete v2 implementation
- **~500 Lines**: CSS theme system
- **~1000 Lines**: Component styles
- **~800 Lines**: Layout system
- **~800 Lines**: Core application logic
- **~1200 Lines**: Service layer
- **~3800 Lines**: Feature modules

### 🎨 Design Specifications

**Colors**
- Dark theme: Deep blue-gray backgrounds with purple accents
- Light theme: Clean white/gray with same accent colors
- Status colors: Green (success), Red (error), Yellow (warning), Blue (info)

**Typography**
- Font family: System UI fonts (Segoe UI, SF Pro, Roboto)
- Font sizes: 12px - 32px responsive scale
- Font weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

**Spacing**
- Scale: 4px, 8px, 16px, 24px, 32px, 48px
- Consistent padding and margins throughout

**Animations**
- Fade in/out: 200ms ease
- Slide animations: 300ms ease
- Hover effects: 150ms ease
- Skeleton shimmer: 1.5s infinite

### 🚀 Getting Started

**Access v2 GUI:**
- Toribot: http://127.0.0.1:8788/v2
- Ostobotti: http://127.0.0.1:8789/v2

**Access v1 GUI (original):**
- Toribot: http://127.0.0.1:8788/
- Ostobotti: http://127.0.0.1:8789/

### 📝 Migration Notes

Users can continue using v1 indefinitely. To try v2:
1. Start your bot as usual
2. Navigate to `/v2` URL instead of root
3. All functionality is equivalent between v1 and v2
4. Settings and data are shared between both versions

### 🐛 Known Limitations

- Logs page shows placeholder content (backend streaming not yet implemented)
- Real-time WebSocket support not yet added (uses polling instead)
- Charts/graphs on stats page not yet implemented
- Authentication/PIN system not yet implemented

### 🔮 Future Enhancements

- Real-time log streaming via WebSocket
- Advanced charts and data visualization
- Authentication system (PIN/token)
- Export functionality for filtered data
- Bulk operations on products
- Keyboard shortcuts
- Drag-and-drop interface elements
- Custom dashboard layouts

### 📄 Files Added

**Structure:**
```
/static/v2/
  ├── index.html                 # Main HTML
  ├── app.js                     # Core application
  ├── config.json                # Configuration
  ├── styles/
  │   ├── theme.css             # Theme system
  │   ├── components.css        # Component styles
  │   └── layout.css            # Layout styles
  ├── services/
  │   ├── api.js                # API client
  │   ├── state.js              # State management
  │   ├── toast.js              # Notifications
  │   └── ui.js                 # UI utilities
  └── features/
      ├── dashboard.js          # Dashboard module
      ├── products.js           # Products module
      ├── logs.js               # Logs module
      └── settings.js           # Settings module
```

### 🙏 Credits

Built with vanilla JavaScript, no frameworks required. Uses:
- Font Awesome 6.4.0 for icons (CDN)
- CSS Grid and Flexbox for layout
- CSS Custom Properties for theming
- Modern JavaScript ES6+ features

---

## Previous Versions

See git history for changes in v1.x releases.
