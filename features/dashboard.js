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
        <h2 class="content-title">${i18n.t('dashboard.title')}</h2>
        <p class="content-description">${i18n.t('dashboard.description')}</p>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-4" id="stats-grid">
        ${this.renderStatsLoading()}
      </div>

      <!-- Quick Actions -->
      <div class="card mt-lg">
        <div class="card-header">
          <h3 class="card-title">${i18n.t('dashboard.quickActions')}</h3>
        </div>
        <div class="card-body">
          <div style="display: flex; gap: var(--space-md); flex-wrap: wrap;">
            <button class="btn btn-primary" onclick="Dashboard.fetchProducts()">
              <i class="fas fa-sync-alt"></i> ${i18n.t('dashboard.fetchProducts')}
            </button>
            <button class="btn btn-primary" onclick="Dashboard.triggerValuation()">
              <i class="fas fa-brain"></i> ${i18n.t('dashboard.runValuation')}
            </button>
            <button class="btn btn-secondary" onclick="Dashboard.refreshAll()">
              <i class="fas fa-redo"></i> ${i18n.t('dashboard.refreshAll')}
            </button>
            <button class="btn btn-secondary" onclick="Dashboard.saveProducts()">
              <i class="fas fa-download"></i> ${i18n.t('dashboard.exportCSV')}
            </button>
          </div>
        </div>
      </div>

      <!-- Real-time Logs -->
      <div class="card mt-lg">
        <div class="card-header">
          <h3 class="card-title">${i18n.t('logs.realtime')}</h3>
          <div style="display: flex; gap: var(--space-sm);">
            <button class="btn btn-sm btn-secondary" onclick="Dashboard.clearLogs()">
              <i class="fas fa-trash"></i> ${i18n.t('logs.clear')}
            </button>
            <button class="btn btn-sm btn-secondary" onclick="Dashboard.downloadLogs()">
              <i class="fas fa-download"></i> ${i18n.t('logs.download')}
            </button>
            <button class="btn btn-sm btn-secondary" onclick="app.navigate('logs')">
              ${i18n.t('dashboard.viewAll')} <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>
        <div class="card-body">
          <div id="real-time-logs" style="
            background: var(--bg-code);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: var(--space-md);
            height: 200px;
            overflow-y: auto;
            font-family: var(--font-mono);
            font-size: var(--text-sm);
            line-height: 1.4;
          ">
            <div class="log-entry log-info">
              <span class="log-timestamp">[${new Date().toLocaleString('fi-FI')}]</span>
              <span class="log-level">[INFO]</span>
              <span class="log-message">Sovellus käynnistetty onnistuneesti</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Products -->
      <div class="card mt-lg">
        <div class="card-header">
          <h3 class="card-title">${i18n.t('dashboard.recentProducts')}</h3>
          <button class="btn btn-sm btn-secondary" onclick="app.navigate('products')">
            ${i18n.t('dashboard.viewAll')} <i class="fas fa-arrow-right"></i>
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
    
    // Add initial log
    setTimeout(() => {
      this.addLog('ToriBot v2 käynnistetty onnistuneesti', 'success');
    }, 100);
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
        label: i18n.t('dashboard.stats.total'),
        color: 'primary',
      },
      {
        icon: 'fa-sparkles',
        value: stats.newToday,
        label: i18n.t('dashboard.stats.newToday'),
        color: 'info',
      },
      {
        icon: 'fa-brain',
        value: stats.withValuation,
        label: i18n.t('dashboard.stats.withValuation'),
        color: 'success',
      },
      {
        icon: 'fa-exclamation-triangle',
        value: stats.errors,
        label: i18n.t('dashboard.stats.errors'),
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
        i18n.t('dashboard.noProducts'),
        i18n.t('dashboard.noProductsDesc'),
        `<button class="btn btn-primary" onclick="Dashboard.fetchProducts()"><i class="fas fa-sync-alt"></i> ${i18n.t('dashboard.fetchProducts')}</button>`
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
    
    // Add event listeners for product cards
    container.querySelectorAll('.product-card').forEach(card => {
      const productId = card.dataset.productId;
      
      card.addEventListener('click', () => {
        if (productId) this.showProductDetail(productId);
      });
      
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          if (productId) this.showProductDetail(productId);
        }
      });
    });
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
      ? `<span class="badge badge-success"><i class="fas fa-check"></i> ${i18n.t('products.valuated')}</span>`
      : '';
    
    // Get worth value
    const worth = product.valuation?.price_current ?? product.valuation?.price_estimate;
    const worthDisplay = worth != null
      ? `<div style="font-size: var(--text-sm); color: var(--primary); font-weight: 600; margin-top: var(--space-xs);">
           <i class="fas fa-tag"></i> ${i18n.t('product.worth')}: ~${worth}€
         </div>`
      : '';

    return `
      <div class="card product-card"
           style="cursor: pointer;"
           role="button"
           tabindex="0"
           data-product-id="${UI.escapeHTML(product.id)}">
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
          <span><i class="fas fa-map-marker-alt"></i> ${UI.escapeHTML(product.location || 'N/A')}</span>
          <span>${UI.formatDate(product.discovered_at)}</span>
        </div>
        ${worthDisplay}
        ${valuationBadge ? `<div style="margin-top: var(--space-sm);">${valuationBadge}</div>` : ''}
      </div>
    `;
  },

  /**
   * Show product detail modal - fixed to handle HTML properly
   */
  showProductDetail(productId) {
    const products = state.get('products');
    const product = products.find(p => p.id === productId);
    
    if (!product) {
      toast.error(i18n.t('product.notFound'));
      return;
    }

    // Create modal structure
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'modal modal-large';
    
    // Header
    const header = document.createElement('div');
    header.className = 'modal-header';
    header.innerHTML = `
      <h3 class="modal-title">${UI.escapeHTML(UI.truncate(product.title, 50))}</h3>
      <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
        <i class="fas fa-times"></i>
      </button>
    `;
    
    // Body with product details
    const body = document.createElement('div');
    body.className = 'modal-body';
    body.style.maxHeight = '70vh';
    body.style.overflowY = 'auto';
    
    const images = product.image_files?.map(img => 
      `<img src="/images/${UI.escapeHTML(img)}" style="width: 100%; border-radius: var(--radius-md); margin-bottom: var(--space-sm);" onerror="this.style.display='none'">`
    ).join('') || `<p style="color: var(--text-muted);">${i18n.t('product.noImages')}</p>`;

    const worth = product.valuation?.price_current ?? product.valuation?.price_estimate;

    const valuation = product.valuation?.status === 'completed'
      ? `
        <div style="background: var(--surface-hover); padding: var(--space-md); border-radius: var(--radius-md); margin-top: var(--space-md);">
          <h4 style="margin-bottom: var(--space-sm);"><i class="fas fa-brain"></i> ${i18n.t('product.valuation')}</h4>
          ${worth ? `<p style="font-size: var(--text-lg); color: var(--primary); font-weight: 600; margin-bottom: var(--space-sm);"><i class="fas fa-tag"></i> ${i18n.t('product.worth')}: ~${worth}€</p>` : ''}
          <p style="white-space: pre-wrap;">${UI.escapeHTML(product.valuation.response || 'No response')}</p>
        </div>
      `
      : `<p style="color: var(--text-muted); margin-top: var(--space-md);">${i18n.t('product.noValuation')}</p>`;

    body.innerHTML = `
      <div style="margin-bottom: var(--space-md);">
        ${images}
      </div>
      <h3 style="margin-bottom: var(--space-sm);">${UI.escapeHTML(product.title)}</h3>
      <p style="color: var(--text-secondary); margin-bottom: var(--space-md);">${UI.escapeHTML(product.description || i18n.t('product.noDescription'))}</p>
      
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-md); margin-bottom: var(--space-md);">
        <div>
          <strong>${i18n.t('product.location')}:</strong><br>
          <span style="color: var(--text-secondary);">${UI.escapeHTML(product.location || 'N/A')}</span>
        </div>
        <div>
          <strong>${i18n.t('product.seller')}:</strong><br>
          <span style="color: var(--text-secondary);">${UI.escapeHTML(product.seller || 'N/A')}</span>
        </div>
        <div>
          <strong>${i18n.t('product.discovered')}:</strong><br>
          <span style="color: var(--text-secondary);">${UI.formatDate(product.discovered_at)}</span>
        </div>
        <div>
          <strong>${i18n.t('product.price')}:</strong><br>
          <span style="color: var(--text-secondary);">${UI.formatPrice(product.price)}</span>
        </div>
      </div>

      ${valuation}
    `;
    
    // Footer
    const footer = document.createElement('div');
    footer.className = 'modal-footer';
    footer.innerHTML = `
      <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">${i18n.t('product.close')}</button>
      <a href="${UI.escapeHTML(product.url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
        <i class="fas fa-external-link-alt"></i> ${i18n.t('product.viewOnTori')}
      </a>
    `;
    
    modal.appendChild(header);
    modal.appendChild(body);
    modal.appendChild(footer);
    modalOverlay.appendChild(modal);
    
    // Close on backdrop click
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) {
        modalOverlay.remove();
      }
    });
    
    // Close on Escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        modalOverlay.remove();
        document.removeEventListener('keydown', handleEscape);
      }
    };
    document.addEventListener('keydown', handleEscape);
    
    document.body.appendChild(modalOverlay);
  },

  /**
   * Add log entry to real-time logs
   */
  addLog(message, level = 'info') {
    const logContainer = document.getElementById('real-time-logs');
    if (!logContainer) return;

    const timestamp = new Date().toLocaleString('fi-FI');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${level}`;
    logEntry.innerHTML = `
      <span class="log-timestamp">[${timestamp}]</span>
      <span class="log-level">[${level.toUpperCase()}]</span>
      <span class="log-message">${UI.escapeHTML(message)}</span>
    `;

    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;

    // Keep only last 50 entries
    while (logContainer.children.length > 50) {
      logContainer.removeChild(logContainer.firstChild);
    }
  },

  /**
   * Clear logs
   */
  clearLogs() {
    const logContainer = document.getElementById('real-time-logs');
    if (logContainer) {
      logContainer.innerHTML = '';
      this.addLog('Lokit tyhjennetty', 'info');
    }
  },

  /**
   * Download logs
   */
  downloadLogs() {
    const logContainer = document.getElementById('real-time-logs');
    if (!logContainer) return;

    const logs = Array.from(logContainer.children)
      .map(entry => entry.textContent)
      .join('\n');
    
    const blob = new Blob([logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `toribot-logs-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    this.addLog('Lokit ladattu onnistuneesti', 'success');
  },

  /**
   * Fetch products
   */
  async fetchProducts() {
    try {
      this.addLog(i18n.t('toast.fetchingProducts'), 'info');
      toast.info(i18n.t('toast.fetchingProducts'));
      const res = await api.fetchProducts();
      
      if (res.success) {
        this.addLog(i18n.t('toast.productsFetched'), 'success');
        toast.success(res.message || i18n.t('toast.productsFetched'));
        
        // Immediately refresh data after fetch
        const productsRes = await api.getProducts();
        if (productsRes.success) {
          state.set('products', productsRes.products || []);
          state.calculateStats();
          this.renderStats();
          this.renderRecentProducts();

          // If user is on Products page, refresh that view as well
          if (app.currentPage === 'products' && typeof Products !== 'undefined' && typeof Products.renderTable === 'function') {
            Products.renderTable();
          }
        }
      } else {
        this.addLog(res.error || i18n.t('toast.fetchError'), 'error');
        toast.error(res.error || i18n.t('toast.fetchError'));
      }
    } catch (error) {
      this.addLog('Virhe haettaessa tuotteita: ' + error.message, 'error');
      toast.error('Virhe haettaessa tuotteita: ' + error.message);
    }
  },

  /**
   * Trigger valuation
   */
  async triggerValuation() {
    try {
      this.addLog(i18n.t('toast.runningValuation'), 'info');
      toast.info(i18n.t('toast.runningValuation'));
      const res = await api.triggerValuation();
      
      if (res.success) {
        this.addLog(res.message || i18n.t('toast.valuationStarted'), 'success');
        toast.success(res.message || i18n.t('toast.valuationStarted'));
      } else {
        this.addLog(res.error || i18n.t('toast.valuationError'), 'error');
        toast.error(res.error || i18n.t('toast.valuationError'));
      }
    } catch (error) {
      this.addLog('Virhe käynnistettäessä arviointia: ' + error.message, 'error');
      toast.error('Virhe käynnistettäessä arviointia: ' + error.message);
    }
  },

  /**
   * Refresh all products
   */
  async refreshAll() {
    try {
      this.addLog(i18n.t('toast.refreshing'), 'info');
      toast.info(i18n.t('toast.refreshing'));
      const res = await api.refreshAll();
      
      if (res.success) {
        this.addLog(res.message || i18n.t('toast.refreshed'), 'success');
        toast.success(res.message || i18n.t('toast.refreshed'));
      } else {
        this.addLog(res.error || 'Päivitys epäonnistui', 'error');
        toast.error(res.error || 'Päivitys epäonnistui');
      }
    } catch (error) {
      this.addLog('Virhe päivitettäessä tuotteita: ' + error.message, 'error');
      toast.error('Virhe päivitettäessä tuotteita: ' + error.message);
    }
  },

  /**
   * Save products to CSV
   */
  async saveProducts() {
    try {
      this.addLog(i18n.t('toast.exporting'), 'info');
      toast.info(i18n.t('toast.exporting'));
      const res = await api.saveProducts();
      
      if (res.success) {
        const message = i18n.t('toast.exported', { count: res.count, filename: res.filename });
        this.addLog(message, 'success');
        toast.success(message);
      } else {
        this.addLog(res.error || i18n.t('toast.exportError'), 'error');
        toast.error(res.error || i18n.t('toast.exportError'));
      }
    } catch (error) {
      this.addLog('Virhe vietäessä tuotteita: ' + error.message, 'error');
      toast.error('Virhe vietäessä tuotteita: ' + error.message);
    }
  },
};
