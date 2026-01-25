// ==========================================================================
// ToriBot v2 - Dashboard Feature
// Main dashboard with stats and recent products
// ==========================================================================

const Dashboard = {
  /**
   * Render dashboard
   */
  render(container) {
    container.innerHTML = `
      <div class="content-header">
        <h2 class="content-title">Dashboard</h2>
        <p class="content-description">Overview of your Tori.fi monitoring bot</p>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-4" id="stats-grid">
        ${this.renderStatsLoading()}
      </div>

      <!-- Quick Actions -->
      <div class="card mt-lg">
        <div class="card-header">
          <h3 class="card-title">Quick Actions</h3>
        </div>
        <div class="card-body">
          <div style="display: flex; gap: var(--space-md); flex-wrap: wrap;">
            <button class="btn btn-primary" onclick="Dashboard.fetchProducts()">
              <i class="fas fa-sync-alt"></i> Fetch New Products
            </button>
            <button class="btn btn-primary" onclick="Dashboard.triggerValuation()">
              <i class="fas fa-brain"></i> Run AI Valuation
            </button>
            <button class="btn btn-secondary" onclick="Dashboard.refreshAll()">
              <i class="fas fa-redo"></i> Refresh All Products
            </button>
            <button class="btn btn-secondary" onclick="Dashboard.saveProducts()">
              <i class="fas fa-download"></i> Export to CSV
            </button>
          </div>
        </div>
      </div>

      <!-- Recent Products -->
      <div class="card mt-lg">
        <div class="card-header">
          <h3 class="card-title">Recent Products</h3>
          <button class="btn btn-sm btn-secondary" onclick="app.navigate('products')">
            View All <i class="fas fa-arrow-right"></i>
          </button>
        </div>
        <div class="card-body">
          <div id="recent-products">
            ${UI.createSkeleton('card', 3)}
          </div>
        </div>
      </div>
    `;

    // Load data
    this.renderStats();
    this.renderRecentProducts();
  },

  /**
   * Render stats loading
   */
  renderStatsLoading() {
    return Array(4).fill(0).map(() => `
      <div class="stat-card">
        <div class="stat-icon skeleton"></div>
        <div class="stat-content">
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-text"></div>
        </div>
      </div>
    `).join('');
  },

  /**
   * Render stats
   */
  renderStats() {
    const stats = state.get('stats');
    const statsGrid = document.getElementById('stats-grid');
    
    if (!statsGrid) return;

    const statCards = [
      {
        icon: 'fa-box',
        value: stats.total,
        label: 'Total Products',
        color: 'primary',
      },
      {
        icon: 'fa-sparkles',
        value: stats.newToday,
        label: 'New Today',
        color: 'info',
      },
      {
        icon: 'fa-brain',
        value: stats.withValuation,
        label: 'AI Valuated',
        color: 'success',
      },
      {
        icon: 'fa-exclamation-triangle',
        value: stats.errors,
        label: 'Errors',
        color: 'warning',
      },
    ];

    statsGrid.innerHTML = statCards.map(stat => `
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas ${stat.icon}"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">${stat.value}</div>
          <div class="stat-label">${stat.label}</div>
        </div>
      </div>
    `).join('');
  },

  /**
   * Render recent products
   */
  renderRecentProducts() {
    const products = state.get('products');
    const container = document.getElementById('recent-products');
    
    if (!container) return;

    if (products.length === 0) {
      container.innerHTML = UI.createEmptyState(
        '<i class="fas fa-box-open"></i>',
        'No products yet',
        'Start by fetching products from Tori.fi',
        '<button class="btn btn-primary" onclick="Dashboard.fetchProducts()"><i class="fas fa-sync-alt"></i> Fetch Products</button>'
      );
      return;
    }

    // Show latest 6 products
    const recent = products.slice(0, 6);
    
    container.innerHTML = `
      <div class="grid grid-cols-3">
        ${recent.map(product => this.renderProductCard(product)).join('')}
      </div>
    `;
  },

  /**
   * Render product card
   */
  renderProductCard(product) {
    const imageUrl = product.image_files?.[0] 
      ? `/images/${product.image_files[0]}`
      : 'https://via.placeholder.com/300x200?text=No+Image';
    
    const hasValuation = product.valuation?.status === 'completed';
    const valuationBadge = hasValuation 
      ? `<span class="badge badge-success"><i class="fas fa-check"></i> Valuated</span>`
      : '';

    return `
      <div class="card" style="cursor: pointer;" onclick="Dashboard.showProductDetail('${product.id}')">
        <img src="${imageUrl}" alt="${UI.escapeHTML(product.title || 'Product')}" 
             style="width: 100%; height: 150px; object-fit: cover; border-radius: var(--radius-md); margin-bottom: var(--space-md);"
             onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
        <h4 style="font-size: var(--text-base); font-weight: 600; margin-bottom: var(--space-sm); color: var(--text-primary);">
          ${UI.escapeHTML(UI.truncate(product.title || '', 50))}
        </h4>
        <p style="font-size: var(--text-sm); color: var(--text-secondary); margin-bottom: var(--space-sm);">
          ${UI.escapeHTML(UI.truncate(product.description || '', 80))}
        </p>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: var(--text-xs); color: var(--text-muted);">
          <span><i class="fas fa-map-marker-alt"></i> ${product.location || 'N/A'}</span>
          <span>${UI.formatDate(product.discovered_at)}</span>
        </div>
        ${valuationBadge ? `<div style="margin-top: var(--space-sm);">${valuationBadge}</div>` : ''}
      </div>
    `;
  },

  /**
   * Show product detail modal
   */
  showProductDetail(productId) {
    const products = state.get('products');
    const product = products.find(p => p.id === productId);
    
    if (!product) {
      toast.error('Product not found');
      return;
    }

    const images = product.image_files?.map(img => 
      `<img src="/images/${img}" style="width: 100%; border-radius: var(--radius-md); margin-bottom: var(--space-sm);" onerror="this.style.display='none'">`
    ).join('') || '<p style="color: var(--text-muted);">No images available</p>';

    const valuation = product.valuation?.status === 'completed'
      ? `
        <div style="background: var(--surface-hover); padding: var(--space-md); border-radius: var(--radius-md); margin-top: var(--space-md);">
          <h4 style="margin-bottom: var(--space-sm);"><i class="fas fa-brain"></i> AI Valuation</h4>
          <p style="white-space: pre-wrap;">${product.valuation.response || 'No response'}</p>
        </div>
      `
      : '<p style="color: var(--text-muted); margin-top: var(--space-md);">No AI valuation yet</p>';

    const content = `
      <div style="max-height: 70vh; overflow-y: auto;">
        <div style="margin-bottom: var(--space-md);">
          ${images}
        </div>
        <h3 style="margin-bottom: var(--space-sm);">${UI.escapeHTML(product.title)}</h3>
        <p style="color: var(--text-secondary); margin-bottom: var(--space-md);">${UI.escapeHTML(product.description || 'No description')}</p>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-md); margin-bottom: var(--space-md);">
          <div>
            <strong>Location:</strong><br>
            <span style="color: var(--text-secondary);">${product.location || 'N/A'}</span>
          </div>
          <div>
            <strong>Seller:</strong><br>
            <span style="color: var(--text-secondary);">${product.seller || 'N/A'}</span>
          </div>
          <div>
            <strong>Discovered:</strong><br>
            <span style="color: var(--text-secondary);">${UI.formatDate(product.discovered_at)}</span>
          </div>
          <div>
            <strong>Price:</strong><br>
            <span style="color: var(--text-secondary);">${UI.formatPrice(product.price)}</span>
          </div>
        </div>

        ${valuation}
      </div>
    `;

    const footer = `
      <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
      <a href="${product.url}" target="_blank" class="btn btn-primary">
        <i class="fas fa-external-link-alt"></i> View on Tori.fi
      </a>
    `;

    UI.showModal(UI.truncate(product.title, 50), content, footer);
  },

  /**
   * Fetch products
   */
  async fetchProducts() {
    try {
      toast.info('Fetching products...');
      const res = await api.fetchProducts();
      
      if (res.success) {
        toast.success(res.message || 'Products fetched successfully');
        
        // Refresh data after a delay
        setTimeout(async () => {
          const productsRes = await api.getProducts();
          if (productsRes.success) {
            state.set('products', productsRes.products || []);
            state.calculateStats();
            this.renderStats();
            this.renderRecentProducts();
          }
        }, 2000);
      } else {
        toast.error(res.error || 'Failed to fetch products');
      }
    } catch (error) {
      toast.error('Error fetching products: ' + error.message);
    }
  },

  /**
   * Trigger valuation
   */
  async triggerValuation() {
    try {
      toast.info('Running AI valuation...');
      const res = await api.triggerValuation();
      
      if (res.success) {
        toast.success(res.message || 'Valuation started');
      } else {
        toast.error(res.error || 'Failed to trigger valuation');
      }
    } catch (error) {
      toast.error('Error triggering valuation: ' + error.message);
    }
  },

  /**
   * Refresh all products
   */
  async refreshAll() {
    try {
      toast.info('Refreshing all products...');
      const res = await api.refreshAll();
      
      if (res.success) {
        toast.success(res.message || 'Refresh started');
      } else {
        toast.error(res.error || 'Failed to refresh products');
      }
    } catch (error) {
      toast.error('Error refreshing products: ' + error.message);
    }
  },

  /**
   * Save products to CSV
   */
  async saveProducts() {
    try {
      toast.info('Exporting products...');
      const res = await api.saveProducts();
      
      if (res.success) {
        toast.success(`Saved ${res.count} products to ${res.filename}`);
      } else {
        toast.error(res.error || 'Failed to save products');
      }
    } catch (error) {
      toast.error('Error saving products: ' + error.message);
    }
  },
};
