// ==========================================================================
// ToriBot v2 - UI Utilities
// Helper functions for UI operations
// ==========================================================================

const UI = {
  /**
   * Format date to human-readable format
   */
  formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('fi-FI', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  },

  /**
   * Format price
   */
  formatPrice(price) {
    if (price === undefined || price === null) return 'N/A';
    if (price === 0 || price === '0') return 'Free';
    return `${price}€`;
  },

  /**
   * Truncate text
   */
  truncate(text, length = 100) {
    if (!text || text.length <= length) return text || '';
    return text.substring(0, length) + '...';
  },

  /**
   * Escape HTML to prevent XSS
   */
  escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },

  /**
   * Create loading skeleton
   */
  createSkeleton(type = 'text', count = 1) {
    let html = '';
    for (let i = 0; i < count; i++) {
      html += `<div class="skeleton skeleton-${type}"></div>`;
    }
    return html;
  },

  /**
   * Create empty state
   */
  createEmptyState(icon, title, message, actionBtn = null) {
    return `
      <div class="empty-state">
        <div class="empty-state-icon">${icon}</div>
        <div class="empty-state-title">${title}</div>
        <div class="empty-state-message">${message}</div>
        ${actionBtn ? `<div class="mt-lg">${actionBtn}</div>` : ''}
      </div>
    `;
  },

  /**
   * Create error state
   */
  createErrorState(title, message, onRetry = null) {
    const retryAttr = onRetry != null
      ? ` data-retry-id="${this.escapeHTML(String(onRetry))}"`
      : '';

    return `
      <div class="error-state">
        <div class="error-state-icon"><i class="fas fa-exclamation-circle"></i></div>
        <div class="error-state-title">${title}</div>
        <div class="error-state-message">${message}</div>
        ${onRetry ? `
          <button class="btn btn-primary mt-md" type="button"${retryAttr}>
            <i class="fas fa-redo"></i> Retry
          </button>
        ` : ''}
      </div>
    `;
  },

  /**
   * Create badge based on status
   */
  createStatusBadge(status) {
    const statusMap = {
      completed: { class: 'success', text: 'Completed', icon: 'check' },
      pending: { class: 'warning', text: 'Pending', icon: 'clock' },
      failed: { class: 'error', text: 'Failed', icon: 'times' },
      running: { class: 'info', text: 'Running', icon: 'spinner spinning' },
      queued: { class: 'neutral', text: 'Queued', icon: 'hourglass' },
    };

    const config = statusMap[status] || statusMap.queued;
    
    return `
      <span class="badge badge-${config.class}">
        <i class="fas fa-${config.icon}"></i>
        ${config.text}
      </span>
    `;
  },

  /**
   * Show modal
   */
  showModal(title, content, footer = null) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    // Build static modal structure without interpolating dynamic content
    modal.innerHTML = `
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title"></h3>
          <button class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body"></div>
        <div class="modal-footer" style="display: none;"></div>
      </div>
    `;

    const titleEl = modal.querySelector('.modal-title');
    const bodyEl = modal.querySelector('.modal-body');
    const footerEl = modal.querySelector('.modal-footer');
    const closeBtn = modal.querySelector('.modal-close');

    if (titleEl && typeof title === 'string') {
      titleEl.textContent = title;
    }

    if (bodyEl) {
      if (content instanceof Node) {
        bodyEl.appendChild(content);
      } else if (Array.isArray(content)) {
        content.forEach((item) => {
          if (item instanceof Node) {
            bodyEl.appendChild(item);
          } else if (typeof item === 'string') {
            const p = document.createElement('p');
            p.textContent = item;
            bodyEl.appendChild(p);
          }
        });
      } else if (typeof content === 'string') {
        // Treat content as plain text to avoid XSS
        bodyEl.textContent = content;
      }
    }

    if (footerEl) {
      if (footer instanceof Node) {
        footerEl.style.display = '';
        footerEl.appendChild(footer);
      } else if (typeof footer === 'string' && footer.trim() !== '') {
        footerEl.style.display = '';
        footerEl.textContent = footer;
      }
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        modal.remove();
      });
    }
    
    // Close on backdrop click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
    
    // Close on Escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        modal.remove();
        document.removeEventListener('keydown', handleEscape);
      }
    };
    document.addEventListener('keydown', handleEscape);
    
    document.body.appendChild(modal);
    return modal;
  },

  /**
   * Show confirmation dialog
   */
  async confirm(title, message) {
    return new Promise((resolve) => {
      const footer = `
        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').dispatchEvent(new CustomEvent('resolve', {detail: false}))">
          Cancel
        </button>
        <button class="btn btn-primary" onclick="this.closest('.modal-overlay').dispatchEvent(new CustomEvent('resolve', {detail: true}))">
          Confirm
        </button>
      `;
      
      const modal = this.showModal(title, `<p>${message}</p>`, footer);
      
      modal.addEventListener('resolve', (e) => {
        resolve(e.detail);
        modal.remove();
      });
    });
  },

  /**
   * Copy text to clipboard
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('Copied to clipboard');
      return true;
    } catch (error) {
      toast.error('Failed to copy to clipboard');
      return false;
    }
  },

  /**
   * Debounce function
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * Throttle function
   */
  throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  },
};
