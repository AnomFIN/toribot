// ==========================================================================
// ToriBot v2 - Settings Feature
// Bot configuration and settings management
// ==========================================================================

const Settings = {
  /**
   * Render settings page
   */
  render(container) {
    const settings = state.get('settings');
    
    if (!settings) {
      container.innerHTML = UI.createErrorState(
        'Settings Not Available',
        'Failed to load settings from the server',
        'app.refresh()'
      );
      return;
    }

    container.innerHTML = `
      <div class="content-header">
        <h2 class="content-title">Settings</h2>
        <p class="content-description">Configure bot behavior and preferences</p>
      </div>

      <form id="settings-form" onsubmit="Settings.saveSettings(event)">
        <!-- General Settings -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title"><i class="fas fa-cog"></i> General Settings</h3>
          </div>
          <div class="card-body">
            <div class="grid grid-cols-2">
              <div class="input-group">
                <label class="input-label">Poll Interval (seconds)</label>
                <input type="number" class="input" name="poll_interval_seconds" 
                       value="${settings.poll_interval_seconds}" min="30" required>
              </div>
              <div class="input-group">
                <label class="input-label">Request Timeout (seconds)</label>
                <input type="number" class="input" name="request_timeout_seconds" 
                       value="${settings.request_timeout_seconds}" min="5" required>
              </div>
              <div class="input-group">
                <label class="input-label">Max Retries</label>
                <input type="number" class="input" name="max_retries" 
                       value="${settings.max_retries}" min="0" max="10" required>
              </div>
              <div class="input-group">
                <label class="input-label">Products Per Page</label>
                <input type="number" class="input" name="products_per_page" 
                       value="${settings.products_per_page}" min="10" required>
              </div>
            </div>
          </div>
        </div>

        <!-- Image Settings -->
        <div class="card mt-lg">
          <div class="card-header">
            <h3 class="card-title"><i class="fas fa-image"></i> Image Settings</h3>
          </div>
          <div class="card-body">
            <div class="grid grid-cols-2">
              <div class="input-group">
                <label style="display: flex; align-items: center; gap: var(--space-sm); cursor: pointer;">
                  <input type="checkbox" name="images.download_enabled" 
                         ${settings.images?.download_enabled ? 'checked' : ''}>
                  <span>Enable Image Download</span>
                </label>
              </div>
              <div class="input-group">
                <label class="input-label">Max Images Per Item</label>
                <input type="number" class="input" name="images.max_images_per_item" 
                       value="${settings.images?.max_images_per_item || 5}" min="1" max="10">
              </div>
            </div>
          </div>
        </div>

        <!-- OpenAI Settings -->
        <div class="card mt-lg">
          <div class="card-header">
            <h3 class="card-title"><i class="fas fa-brain"></i> OpenAI Settings</h3>
          </div>
          <div class="card-body">
            <div class="grid grid-cols-2">
              <div class="input-group">
                <label style="display: flex; align-items: center; gap: var(--space-sm); cursor: pointer;">
                  <input type="checkbox" name="openai.enabled" 
                         ${settings.openai?.enabled ? 'checked' : ''}>
                  <span>Enable OpenAI Valuation</span>
                </label>
              </div>
              <div class="input-group">
                <label class="input-label">Valuation Interval (minutes)</label>
                <input type="number" class="input" name="openai.valuation_interval_minutes" 
                       value="${settings.openai?.valuation_interval_minutes || 60}" min="5">
              </div>
              <div class="input-group" style="grid-column: 1 / -1;">
                <label class="input-label">API Key</label>
                <input type="password" class="input" name="openai.api_key" 
                       placeholder="sk-..." 
                       value="${settings.openai?.api_key === '***MASKED***' ? '' : settings.openai?.api_key || ''}">
                <small style="color: var(--text-muted); font-size: var(--text-xs); margin-top: var(--space-xs); display: block;">
                  Leave empty to keep current key
                </small>
              </div>
              <div class="input-group">
                <label class="input-label">Model</label>
                <select class="select" name="openai.model">
                  <option value="gpt-4o-mini" ${settings.openai?.model === 'gpt-4o-mini' ? 'selected' : ''}>GPT-4o Mini</option>
                  <option value="gpt-4o" ${settings.openai?.model === 'gpt-4o' ? 'selected' : ''}>GPT-4o</option>
                  <option value="gpt-4" ${settings.openai?.model === 'gpt-4' ? 'selected' : ''}>GPT-4</option>
                  <option value="gpt-3.5-turbo" ${settings.openai?.model === 'gpt-3.5-turbo' ? 'selected' : ''}>GPT-3.5 Turbo</option>
                </select>
              </div>
              <div class="input-group">
                <label class="input-label">Base URL</label>
                <input type="text" class="input" name="openai.base_url" 
                       value="${settings.openai?.base_url || 'https://api.openai.com/v1'}">
              </div>
            </div>
          </div>
        </div>

        <!-- Server Settings -->
        <div class="card mt-lg">
          <div class="card-header">
            <h3 class="card-title"><i class="fas fa-server"></i> Server Settings</h3>
          </div>
          <div class="card-body">
            <div class="grid grid-cols-2">
              <div class="input-group">
                <label class="input-label">Host</label>
                <input type="text" class="input" name="server.host" 
                       value="${settings.server?.host || '127.0.0.1'}" required>
              </div>
              <div class="input-group">
                <label class="input-label">Port</label>
                <input type="number" class="input" name="server.port" 
                       value="${settings.server?.port || 8788}" min="1024" max="65535" required>
              </div>
            </div>
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: var(--radius-md); padding: var(--space-md); margin-top: var(--space-md);">
              <p style="color: var(--warning); margin: 0; font-size: var(--text-sm);">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Note:</strong> Server settings require bot restart to take effect.
              </p>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="mt-lg" style="display: flex; gap: var(--space-md); justify-content: flex-end;">
          <button type="button" class="btn btn-secondary" onclick="Settings.resetForm()">
            <i class="fas fa-undo"></i> Reset
          </button>
          <button type="submit" class="btn btn-primary">
            <i class="fas fa-save"></i> Save Settings
          </button>
        </div>
      </form>
    `;
  },

  /**
   * Save settings
   */
  async saveSettings(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Build settings object
    const newSettings = {};
    
    // Parse form data
    for (const [key, value] of formData.entries()) {
      const keys = key.split('.');
      let current = newSettings;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
      }
      
      const lastKey = keys[keys.length - 1];
      
      // Parse value type
      if (value === 'on') {
        current[lastKey] = true;
      } else if (!isNaN(value) && value !== '') {
        current[lastKey] = Number(value);
      } else {
        current[lastKey] = value;
      }
    }

    // Handle checkboxes that aren't in formData when unchecked
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
      if (!formData.has(checkbox.name)) {
        const keys = checkbox.name.split('.');
        let current = newSettings;
        for (let i = 0; i < keys.length - 1; i++) {
          if (!current[keys[i]]) current[keys[i]] = {};
          current = current[keys[i]];
        }
        current[keys[keys.length - 1]] = false;
      }
    });

    // Merge with existing settings
    const currentSettings = state.get('settings');
    const mergedSettings = this.deepMerge(currentSettings, newSettings);

    // Prepare payload for API:
    // - If openai.api_key is empty or masked, omit it so the server keeps the existing key.
    const payload = JSON.parse(JSON.stringify(mergedSettings));
    if (
      payload &&
      payload.openai &&
      (payload.openai.api_key === '' || payload.openai.api_key === '***MASKED***')
    ) {
      delete payload.openai.api_key;
    }

    try {
      toast.info('Saving settings...');
      const res = await api.updateSettings(payload);
      
      if (res.success) {
        state.set('settings', mergedSettings);
        toast.success('Settings saved successfully');
      } else {
        toast.error(res.error || 'Failed to save settings');
      }
    } catch (error) {
      toast.error('Error saving settings: ' + error.message);
    }
  },

  /**
   * Reset form to current settings
   */
  resetForm() {
    const currentPage = state.get('currentPage');
    if (currentPage === 'settings') {
      app.renderPage('settings');
      toast.info('Form reset to saved values');
    }
  },

  /**
   * Deep merge objects
   */
  deepMerge(target, source) {
    const result = { ...target };
    
    for (const key in source) {
      if (source[key] instanceof Object && !Array.isArray(source[key])) {
        result[key] = this.deepMerge(result[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }
    
    return result;
  },
};
