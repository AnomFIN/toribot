// ==========================================================================
// ToriBot v2 - Products Feature
// Product listing with filters, search, and pagination
// ==========================================================================

const Products = {
  viewMode: 'grid', // 'grid' or 'table'

  /**
   * Render products page
   */
  render(container) {
    container.innerHTML = `
      <div class="content-header">
        <h2 class="content-title">Products</h2>
        <p class="content-description">Browse and manage discovered products</p>
      </div>

      <!-- Filters -->
      <div class="card">
        <div class="card-body">
          <div class="grid grid-cols-4">
            <div class="input-group">
              <label class="input-label">Search</label>
              <input type="text" class="input" placeholder="Search products..." 
                     id="filter-search" value="${state.get('filters.search') || ''}">
            </div>
            <div class="input-group">
              <label class="input-label">Location</label>
              <input type="text" class="input" placeholder="Location" 
                     id="filter-location" value="${state.get('filters.location') || ''}">
            </div>
            <div class="input-group">
              <label class="input-label">Date From</label>
              <input type="date" class="input" id="filter-date-from" 
                     value="${state.get('filters.dateFrom') || ''}">
            </div>
            <div class="input-group">
              <label class="input-label">Has Valuation</label>
              <select class="select" id="filter-valuation">
                <option value="">All</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>
          </div>
          <div style="margin-top: var(--space-md); display: flex; gap: var(--space-sm);">
            <button class="btn btn-primary" onclick="Products.applyFilters()">
              <i class="fas fa-filter"></i> Apply Filters
            </button>
            <button class="btn btn-secondary" onclick="Products.clearFilters()">
              <i class="fas fa-times"></i> Clear
            </button>
            <div style="margin-left: auto; display: flex; gap: var(--space-sm);">
              <button class="btn btn-secondary btn-icon" onclick="Products.setViewMode('grid')" 
                      title="Grid view" id="view-grid">
                <i class="fas fa-th"></i>
              </button>
              <button class="btn btn-secondary btn-icon" onclick="Products.setViewMode('table')" 
                      title="Table view" id="view-table">
                <i class="fas fa-list"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Products Container -->
      <div id="products-container" class="mt-lg">
        ${UI.createSkeleton('card', 6)}
      </div>

      <!-- Pagination -->
      <div class="pagination" id="pagination"></div>
    `;

    // Setup filter listeners
    this.setupFilterListeners();

    // Render products
    this.renderTable();
  },

  /**
   * Setup filter listeners
   */
  setupFilterListeners() {
    const filters = ['search', 'location', 'date-from', 'valuation'];
    filters.forEach(filter => {
      const element = document.getElementById(`filter-${filter}`);
      if (element) {
        element.addEventListener('change', UI.debounce(() => this.applyFilters(), 300));
      }
    });
  },

  /**
   * Apply filters
   */
  applyFilters() {
    const filters = {
      search: document.getElementById('filter-search')?.value || '',
      location: document.getElementById('filter-location')?.value || '',
      dateFrom: document.getElementById('filter-date-from')?.value || '',
      hasValuation: document.getElementById('filter-valuation')?.value || null,
    };

    if (filters.hasValuation !== null) {
      filters.hasValuation = filters.hasValuation === 'true';
    }

    state.update({
      'filters.search': filters.search,
      'filters.location': filters.location,
      'filters.dateFrom': filters.dateFrom,
      'filters.hasValuation': filters.hasValuation,
      'pagination.currentPage': 1, // Reset to first page
    });

    this.renderTable();
  },

  /**
   * Clear filters
   */
  clearFilters() {
    state.update({
      'filters.search': '',
      'filters.location': '',
      'filters.dateFrom': '',
      'filters.dateTo': '',
      'filters.hasValuation': null,
      'pagination.currentPage': 1,
    });

    document.getElementById('filter-search').value = '';
    document.getElementById('filter-location').value = '';
    document.getElementById('filter-date-from').value = '';
    document.getElementById('filter-valuation').value = '';

    this.renderTable();
  },

  /**
   * Set view mode
   */
  setViewMode(mode) {
    this.viewMode = mode;
    document.getElementById('view-grid')?.classList.toggle('btn-primary', mode === 'grid');
    document.getElementById('view-table')?.classList.toggle('btn-primary', mode === 'table');
    this.renderTable();
  },

  /**
   * Render products table/grid
   */
  renderTable() {
    const products = state.getPaginatedProducts();
    const container = document.getElementById('products-container');
    
    if (!container) return;

    if (products.length === 0) {
      container.innerHTML = UI.createEmptyState(
        '<i class="fas fa-box-open"></i>',
        'No products found',
        'Try adjusting your filters or fetch new products',
        '<button class="btn btn-primary" onclick="Dashboard.fetchProducts()"><i class="fas fa-sync-alt"></i> Fetch Products</button>'
      );
      this.renderPagination();
      return;
    }

    if (this.viewMode === 'grid') {
      container.innerHTML = `
        <div class="grid grid-cols-3">
          ${products.map(p => Dashboard.renderProductCard(p)).join('')}
        </div>
      `;
    } else {
      container.innerHTML = this.renderTableView(products);
      
      // Add event listeners for product detail buttons
      container.querySelectorAll('.product-detail-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const productId = e.currentTarget.dataset.productId;
          if (productId) Dashboard.showProductDetail(productId);
        });
      });
    }

    this.renderPagination();
  },

  /**
   * Render table view
   */
  renderTableView(products) {
    return `
      <table class="table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Location</th>
            <th>Price</th>
            <th>Discovered</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${products.map(p => `
            <tr>
              <td>
                <div style="display: flex; align-items: center; gap: var(--space-sm);">
                  ${p.image_files?.[0] ? `
                    <img src="/images/${UI.escapeHTML(p.image_files[0])}" 
                         style="width: 50px; height: 50px; object-fit: cover; border-radius: var(--radius-sm);"
                         onerror="this.style.display='none'">
                  ` : ''}
                  <div>
                    <div style="font-weight: 500;">${UI.escapeHTML(UI.truncate(p.title || '', 40))}</div>
                    <div style="font-size: var(--text-xs); color: var(--text-muted);">${UI.escapeHTML(p.seller || 'N/A')}</div>
                  </div>
                </div>
              </td>
              <td>${UI.escapeHTML(p.location || 'N/A')}</td>
              <td>${UI.formatPrice(p.price)}</td>
              <td>${UI.formatDate(p.discovered_at)}</td>
              <td>${UI.createStatusBadge(p.valuation?.status || 'pending')}</td>
              <td>
                <div style="display: flex; gap: var(--space-xs);">
                  <button class="btn btn-sm btn-secondary product-detail-btn" data-product-id="${UI.escapeHTML(p.id)}" 
                          title="View details">
                    <i class="fas fa-eye"></i>
                  </button>
                  <a href="${UI.escapeHTML(p.url)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-secondary" 
                     title="Open on Tori.fi">
                    <i class="fas fa-external-link-alt"></i>
                  </a>
                </div>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  },

  /**
   * Render pagination
   */
  renderPagination() {
    const pagination = state.get('pagination');
    const container = document.getElementById('pagination');
    
    if (!container || pagination.totalPages <= 1) {
      if (container) container.innerHTML = '';
      return;
    }

    const { currentPage, totalPages } = pagination;
    let pages = [];

    // Always show first page
    pages.push(1);

    // Show pages around current
    for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
      pages.push(i);
    }

    // Always show last page
    if (totalPages > 1) pages.push(totalPages);

    // Remove duplicates and sort
    pages = [...new Set(pages)].sort((a, b) => a - b);

    container.innerHTML = `
      <button class="pagination-btn" onclick="Products.goToPage(${currentPage - 1})" 
              ${currentPage === 1 ? 'disabled' : ''}>
        <i class="fas fa-chevron-left"></i>
      </button>
      
      ${pages.map((page, index) => {
        const showEllipsis = index > 0 && page - pages[index - 1] > 1;
        return `
          ${showEllipsis ? '<span style="padding: 0 var(--space-sm);">...</span>' : ''}
          <button class="pagination-btn ${page === currentPage ? 'active' : ''}" 
                  onclick="Products.goToPage(${page})">
            ${page}
          </button>
        `;
      }).join('')}
      
      <button class="pagination-btn" onclick="Products.goToPage(${currentPage + 1})" 
              ${currentPage === totalPages ? 'disabled' : ''}>
        <i class="fas fa-chevron-right"></i>
      </button>
    `;
  },

  /**
   * Go to page
   */
  goToPage(page) {
    const totalPages = state.get('pagination.totalPages');
    if (page < 1 || page > totalPages) return;
    
    state.set('pagination.currentPage', page);
    this.renderTable();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  },
};
