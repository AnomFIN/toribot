// ==========================================================================
// ToriBot v2 - Toast Notification System
// Shows user-friendly notifications
// ==========================================================================

class ToastService {
  constructor() {
    this.container = null;
    this.toasts = [];
    this.init();
  }

  /**
   * Initialize toast container
   */
  init() {
    this.container = document.createElement('div');
    this.container.className = 'toast-container';
    document.body.appendChild(this.container);
  }

  /**
   * Show a toast notification
   */
  show(message, type = 'info', duration = 4000, title = null) {
    const toast = this.createToast(message, type, title);
    this.container.appendChild(toast);
    this.toasts.push(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto dismiss
    if (duration > 0) {
      setTimeout(() => this.dismiss(toast), duration);
    }

    return toast;
  }

  /**
   * Create toast element
   */
  createToast(message, type, title) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = this.getIcon(type);
    const toastTitle = title || this.getDefaultTitle(type);

    // Icon (trusted HTML for the icon only)
    const iconElement = document.createElement('div');
    iconElement.className = 'toast-icon';
    iconElement.innerHTML = icon;

    // Content container
    const contentElement = document.createElement('div');
    contentElement.className = 'toast-content';

    // Optional title (untrusted content as text)
    if (toastTitle) {
      const titleElement = document.createElement('div');
      titleElement.className = 'toast-title';
      titleElement.textContent = toastTitle;
      contentElement.appendChild(titleElement);
    }

    // Message (untrusted content as text)
    const messageElement = document.createElement('div');
    messageElement.className = 'toast-message';
    messageElement.textContent = message;
    contentElement.appendChild(messageElement);

    // Close button
    const closeButton = document.createElement('button');
    closeButton.className = 'toast-close';
    closeButton.type = 'button';
    closeButton.innerHTML = '<i class="fas fa-times"></i>';
    closeButton.addEventListener('click', () => this.dismiss(toast));

    // Assemble toast
    toast.appendChild(iconElement);
    toast.appendChild(contentElement);
    toast.appendChild(closeButton);
    return toast;
  }

  /**
   * Dismiss a toast
   */
  dismiss(toastElement) {
    toastElement.style.animation = 'slideOutRight 0.2s ease';
    setTimeout(() => {
      if (toastElement.parentNode) {
        toastElement.parentNode.removeChild(toastElement);
      }
      const index = this.toasts.indexOf(toastElement);
      if (index > -1) {
        this.toasts.splice(index, 1);
      }
    }, 200);
  }

  /**
   * Get icon for toast type
   */
  getIcon(type) {
    const icons = {
      success: '<i class="fas fa-check-circle"></i>',
      error: '<i class="fas fa-exclamation-circle"></i>',
      warning: '<i class="fas fa-exclamation-triangle"></i>',
      info: '<i class="fas fa-info-circle"></i>',
    };
    return icons[type] || icons.info;
  }

  /**
   * Get default title for toast type
   */
  getDefaultTitle(type) {
    const titles = {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info',
    };
    return titles[type] || '';
  }

  /**
   * Convenience methods
   */
  success(message, title = null, duration = 4000) {
    return this.show(message, 'success', duration, title);
  }

  error(message, title = null, duration = 6000) {
    return this.show(message, 'error', duration, title);
  }

  warning(message, title = null, duration = 5000) {
    return this.show(message, 'warning', duration, title);
  }

  info(message, title = null, duration = 4000) {
    return this.show(message, 'info', duration, title);
  }

  /**
   * Clear all toasts
   */
  clearAll() {
    this.toasts.forEach(toast => this.dismiss(toast));
  }
}

// Add slideOutRight animation
const style = document.createElement('style');
style.textContent = `
  @keyframes slideOutRight {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// Export singleton instance
const toast = new ToastService();
