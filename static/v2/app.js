// ==========================================================================
// ToriBot v2 - Main Application
// Application initialization and core functionality
// ==========================================================================

class App {
  constructor() {
    this.currentPage = 'dashboard';
    this.initialized = false;
    this.pollingIntervals = {
      status: null,
      products: null,
    };
  }

  /**
   * Initialize the application
   */
  async init() {
    if (this.initialized) return;

    console.log('🚀 Initializing ToriBot v2...');

    // Setup event listeners
    this.setupEventListeners();

    // Apply theme
    this.applyTheme();

    // Load initial data
    await this.loadInitialData();

    // Start polling
    this.startPolling();

    // Show initial page
    this.navigate('dashboard');

    this.initialized = true;
    console.log('✅ ToriBot v2 initialized');
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    sidebarToggle?.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      state.set('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    });

    // Mobile menu toggle
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const backdrop = document.getElementById('sidebar-backdrop');
    mobileToggle?.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      backdrop.classList.toggle('show');
    });
    backdrop?.addEventListener('click', () => {
      sidebar.classList.remove('open');
      backdrop.classList.remove('show');
    });

    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    themeToggle?.addEventListener('click', () => this.toggleTheme());

    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = link.dataset.page;
        if (page) this.navigate(page);
      });
    });

    // Global search
    const globalSearch = document.getElementById('global-search');
    globalSearch?.addEventListener('input', UI.debounce((e) => {
      state.set('filters.search', e.target.value);
      if (this.currentPage === 'products') {
        Dashboard.renderProducts();
      }
    }, 300));

    // Restore sidebar state
    if (state.get('sidebarCollapsed')) {
      sidebar.classList.add('collapsed');
    }
  }

  /**
   * Apply theme
   */
  applyTheme() {
    const theme = state.get('theme');
    document.documentElement.setAttribute('data-theme', theme);
    
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      const icon = themeToggle.querySelector('i');
      const text = themeToggle.querySelector('span');
      if (theme === 'dark') {
        icon.className = 'fas fa-moon';
        text.textContent = 'Dark Mode';
      } else {
        icon.className = 'fas fa-sun';
        text.textContent = 'Light Mode';
      }
    }
  }

  /**
   * Toggle theme
   */
  toggleTheme() {
    const currentTheme = state.get('theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    state.set('theme', newTheme);
    this.applyTheme();
    toast.info(`Theme switched to ${newTheme} mode`);
  }

  /**
   * Navigate to a page
   */
  navigate(page) {
    this.currentPage = page;
    state.set('currentPage', page);

    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.remove('active');
      if (link.dataset.page === page) {
        link.classList.add('active');
      }
    });

    // Update page title
    const titles = {
      dashboard: 'Dashboard',
      products: 'Products',
      logs: 'Logs',
      settings: 'Settings',
    };
    document.getElementById('page-title').textContent = titles[page] || page;

    // Close mobile menu
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    sidebar.classList.remove('open');
    backdrop.classList.remove('show');

    // Render page content
    this.renderPage(page);
  }

  /**
   * Render page content
   */
  renderPage(page) {
    const content = document.getElementById('content');
    
    switch (page) {
      case 'dashboard':
        Dashboard.render(content);
        break;
      case 'products':
        Products.render(content);
        break;
      case 'logs':
        Logs.render(content);
        break;
      case 'settings':
        Settings.render(content);
        break;
      default:
        content.innerHTML = UI.createEmptyState(
          '<i class="fas fa-question-circle"></i>',
          'Page not found',
          `The page "${page}" does not exist.`
        );
    }
  }

  /**
   * Load initial data
   */
  async loadInitialData() {
    try {
      state.set('loading', true);
      
      // Load products and settings in parallel
      const [productsRes, settingsRes] = await Promise.all([
        api.getProducts().catch(err => ({ success: false, error: err.message })),
        api.getSettings().catch(err => ({ success: false, error: err.message })),
      ]);

      if (productsRes.success) {
        state.set('products', productsRes.products || []);
        state.calculateStats();
      }

      if (settingsRes.success) {
        state.set('settings', settingsRes.settings);
      }

      // Check health status
      await this.checkHealth();
      
      state.set('loading', false);
    } catch (error) {
      console.error('Error loading initial data:', error);
      state.set('loading', false);
      state.set('error', error.message);
      toast.error('Failed to load initial data');
    }
  }

  /**
   * Check bot health
   */
  async checkHealth() {
    try {
      const health = await api.getHealth();
      const statusIndicator = document.getElementById('status-indicator');
      const statusText = document.getElementById('status-text');
      
      if (health.success || health.status === 'running') {
        state.set('botStatus', 'online');
        statusIndicator.classList.remove('offline');
        statusText.textContent = 'Online';
      } else {
        state.set('botStatus', 'offline');
        statusIndicator.classList.add('offline');
        statusText.textContent = 'Offline';
      }
    } catch (error) {
      state.set('botStatus', 'offline');
      const statusIndicator = document.getElementById('status-indicator');
      const statusText = document.getElementById('status-text');
      statusIndicator.classList.add('offline');
      statusText.textContent = 'Offline';
    }
  }

  /**
   * Start polling for updates
   */
  startPolling() {
    // Status polling (every 5 seconds)
    this.pollingIntervals.status = setInterval(() => {
      this.checkHealth();
    }, 5000);

    // Products polling (every 30 seconds)
    this.pollingIntervals.products = setInterval(async () => {
      try {
        const res = await api.getProducts();
        if (res.success) {
          state.set('products', res.products || []);
          state.calculateStats();
          
          // Refresh current page if it's dashboard or products
          if (this.currentPage === 'dashboard') {
            Dashboard.renderStats();
          } else if (this.currentPage === 'products') {
            Products.renderTable();
          }
        }
      } catch (error) {
        console.error('Error polling products:', error);
      }
    }, 30000);
  }

  /**
   * Stop polling
   */
  stopPolling() {
    Object.values(this.pollingIntervals).forEach(interval => {
      if (interval) clearInterval(interval);
    });
  }

  /**
   * Refresh all data
   */
  async refresh() {
    toast.info('Refreshing data...');
    await this.loadInitialData();
    this.renderPage(this.currentPage);
    toast.success('Data refreshed');
  }
}

// Create global app instance
const app = new App();

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => app.init());
} else {
  app.init();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  app.stopPolling();
});
