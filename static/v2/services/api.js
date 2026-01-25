// ==========================================================================
// ToriBot v2 - API Service
// Handles all API communication with backend
// ==========================================================================

class APIService {
  constructor(baseURL = '') {
    this.baseURL = baseURL;
    this.timeout = 15000; // 15 seconds
  }

  /**
   * Generic fetch wrapper with timeout and error handling
   * Note: Retry logic not yet implemented - handled by backend endpoints
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      throw error;
    }
  }

  /**
   * GET request
   */
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  /**
   * POST request
   */
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * DELETE request
   */
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // ==========================================================================
  // Bot API Endpoints
  // ==========================================================================

  /**
   * Get all products
   */
  async getProducts() {
    return this.get('/api/products');
  }

  /**
   * Get settings
   */
  async getSettings() {
    return this.get('/api/settings');
  }

  /**
   * Update settings
   */
  async updateSettings(settings) {
    return this.post('/api/settings', settings);
  }

  /**
   * Trigger manual valuation
   */
  async triggerValuation() {
    return this.post('/api/valuate', {});
  }

  /**
   * Trigger product fetch
   */
  async fetchProducts(numProducts = null) {
    return this.post('/api/fetch', { num_products: numProducts });
  }

  /**
   * Save products to CSV
   */
  async saveProducts() {
    return this.post('/api/save', {});
  }

  /**
   * Refresh all products
   */
  async refreshAll() {
    return this.post('/api/refresh-all', {});
  }

  /**
   * Fetch images
   */
  async fetchImages() {
    return this.post('/api/fetch-images', {});
  }

  /**
   * Check bot health (custom endpoint to be added)
   */
  async getHealth() {
    try {
      const response = await this.get('/api/health');
      return response;
    } catch (error) {
      return { success: false, status: 'offline', error: error.message };
    }
  }
}

// Export singleton instance
const api = new APIService();
