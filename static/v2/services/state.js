// ==========================================================================
// ToriBot v2 - State Management
// Simple reactive state management for the application
// ==========================================================================

class StateManager {
  constructor() {
    this.state = {
      // App state
      theme: 'dark',
      sidebarCollapsed: false,
      currentPage: 'dashboard',
      
      // Bot state
      botStatus: 'unknown',
      lastUpdate: null,
      
      // Data state
      products: [],
      settings: null,
      stats: {
        total: 0,
        withValuation: 0,
        newToday: 0,
        errors: 0,
      },
      
      // UI state
      loading: false,
      error: null,
      
      // Filters
      filters: {
        search: '',
        location: '',
        dateFrom: '',
        dateTo: '',
        hasValuation: null,
      },
      
      // Pagination
      pagination: {
        currentPage: 1,
        itemsPerPage: 20,
        totalPages: 1,
      },
    };
    
    this.listeners = new Map();
    this.loadPersistedState();
  }

  /**
   * Get state value
   */
  get(key) {
    return key.split('.').reduce((obj, k) => obj?.[k], this.state);
  }

  /**
   * Set state value and notify listeners
   */
  set(key, value) {
    const keys = key.split('.');
    const lastKey = keys.pop();
    const target = keys.reduce((obj, k) => {
      if (!obj[k]) obj[k] = {};
      return obj[k];
    }, this.state);
    
    target[lastKey] = value;
    this.notify(key, value);
    this.persistState(key, value);
  }

  /**
   * Update multiple state values
   */
  update(updates) {
    Object.entries(updates).forEach(([key, value]) => {
      this.set(key, value);
    });
  }

  /**
   * Subscribe to state changes
   */
  subscribe(key, callback) {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, new Set());
    }
    this.listeners.get(key).add(callback);
    
    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(key);
      if (callbacks) {
        callbacks.delete(callback);
      }
    };
  }

  /**
   * Notify all listeners for a key
   */
  notify(key, value) {
    const callbacks = this.listeners.get(key);
    if (callbacks) {
      callbacks.forEach(callback => callback(value));
    }
    
    // Also notify wildcard listeners
    const wildcardCallbacks = this.listeners.get('*');
    if (wildcardCallbacks) {
      wildcardCallbacks.forEach(callback => callback(key, value));
    }
  }

  /**
   * Load persisted state from localStorage
   */
  loadPersistedState() {
    try {
      const theme = localStorage.getItem('toribot_theme');
      if (theme) this.state.theme = theme;
      
      const sidebarCollapsed = localStorage.getItem('toribot_sidebar_collapsed');
      if (sidebarCollapsed) this.state.sidebarCollapsed = sidebarCollapsed === 'true';
      
      const filters = localStorage.getItem('toribot_filters');
      if (filters) this.state.filters = JSON.parse(filters);
    } catch (error) {
      console.error('Error loading persisted state:', error);
    }
  }

  /**
   * Persist state to localStorage
   */
  persistState(key, value) {
    try {
      if (key === 'theme') {
        localStorage.setItem('toribot_theme', value);
      } else if (key === 'sidebarCollapsed') {
        localStorage.setItem('toribot_sidebar_collapsed', value);
      } else if (key.startsWith('filters')) {
        localStorage.setItem('toribot_filters', JSON.stringify(this.state.filters));
      }
    } catch (error) {
      console.error('Error persisting state:', error);
    }
  }

  /**
   * Calculate statistics from products
   */
  calculateStats() {
    const products = this.state.products;
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    this.state.stats = {
      total: products.length,
      withValuation: products.filter(p => p.valuation?.status === 'completed').length,
      newToday: products.filter(p => {
        const discovered = new Date(p.discovered_at);
        return discovered >= today;
      }).length,
      errors: products.filter(p => p.extraction_errors > 0).length,
    };
    
    this.notify('stats', this.state.stats);
  }

  /**
   * Get filtered products
   */
  getFilteredProducts() {
    let filtered = [...this.state.products];
    const { search, location, dateFrom, dateTo, hasValuation } = this.state.filters;
    
    // Search filter
    if (search) {
      const searchLower = search.toLowerCase();
      filtered = filtered.filter(p =>
        p.title?.toLowerCase().includes(searchLower) ||
        p.description?.toLowerCase().includes(searchLower)
      );
    }
    
    // Location filter
    if (location) {
      const locationLower = location.toLowerCase();
      filtered = filtered.filter(p =>
        p.location?.toLowerCase().includes(locationLower)
      );
    }
    
    // Date filters
    if (dateFrom) {
      const from = new Date(dateFrom);
      filtered = filtered.filter(p => new Date(p.discovered_at) >= from);
    }
    
    if (dateTo) {
      const to = new Date(dateTo);
      filtered = filtered.filter(p => new Date(p.discovered_at) <= to);
    }
    
    // Valuation filter
    if (hasValuation !== null) {
      filtered = filtered.filter(p => {
        const hasVal = p.valuation?.status === 'completed';
        return hasValuation ? hasVal : !hasVal;
      });
    }
    
    return filtered;
  }

  /**
   * Get paginated products
   */
  getPaginatedProducts() {
    const filtered = this.getFilteredProducts();
    const { currentPage, itemsPerPage } = this.state.pagination;
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    
    this.state.pagination.totalPages = Math.ceil(filtered.length / itemsPerPage);
    
    return filtered.slice(start, end);
  }
}

// Export singleton instance
const state = new StateManager();
