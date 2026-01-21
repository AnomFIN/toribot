// ==========================================================================
// ToriBot v2 - Logs Feature
// Log viewer with filtering and real-time updates
// ==========================================================================

const Logs = {
  autoScroll: true,
  logLevel: 'all',

  /**
   * Render logs page
   */
  render(container) {
    container.innerHTML = `
      <div class="content-header">
        <h2 class="content-title">Logs</h2>
        <p class="content-description">View bot activity logs</p>
      </div>

      <!-- Log Controls -->
      <div class="card">
        <div class="card-body">
          <div style="display: flex; justify-content: space-between; align-items: center; gap: var(--space-md);">
            <div style="display: flex; gap: var(--space-md); align-items: center;">
              <div class="input-group" style="margin-bottom: 0;">
                <label class="input-label">Level</label>
                <select class="select" id="log-level-filter" onchange="Logs.setLogLevel(this.value)">
                  <option value="all">All</option>
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                </select>
              </div>
              <label style="display: flex; align-items: center; gap: var(--space-sm); cursor: pointer;">
                <input type="checkbox" id="auto-scroll" checked onchange="Logs.toggleAutoScroll(this.checked)">
                <span>Auto-scroll</span>
              </label>
            </div>
            <div style="display: flex; gap: var(--space-sm);">
              <button class="btn btn-secondary" onclick="Logs.refresh()">
                <i class="fas fa-sync-alt"></i> Refresh
              </button>
              <button class="btn btn-secondary" onclick="Logs.copyLogs()">
                <i class="fas fa-copy"></i> Copy
              </button>
              <button class="btn btn-secondary" onclick="Logs.clearLogs()">
                <i class="fas fa-trash"></i> Clear
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Log Viewer -->
      <div class="card mt-lg">
        <div class="card-body">
          <div id="log-viewer" style="
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: var(--space-md);
            font-family: var(--font-mono);
            font-size: var(--text-sm);
            max-height: 600px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
          ">
            ${UI.createEmptyState(
              '<i class="fas fa-file-alt"></i>',
              'No logs available',
              'Logs will appear here as the bot runs'
            )}
          </div>
        </div>
      </div>
    `;

    this.loadLogs();
  },

  /**
   * Set log level filter
   */
  setLogLevel(level) {
    this.logLevel = level;
    this.loadLogs();
  },

  /**
   * Toggle auto-scroll
   */
  toggleAutoScroll(enabled) {
    this.autoScroll = enabled;
  },

  /**
   * Load logs (simulated - real implementation would fetch from backend)
   */
  async loadLogs() {
    const viewer = document.getElementById('log-viewer');
    if (!viewer) return;

    // This is a placeholder. In a real implementation, you would:
    // 1. Add a /api/logs endpoint to the backend
    // 2. Fetch logs from the debug directory
    // 3. Stream logs in real-time using WebSocket or polling

    const sampleLogs = this.generateSampleLogs();
    
    viewer.innerHTML = `<div style="color: var(--text-secondary);">${sampleLogs}</div>`;

    if (this.autoScroll) {
      viewer.scrollTop = viewer.scrollHeight;
    }
  },

  /**
   * Generate sample logs for demonstration
   */
  generateSampleLogs() {
    const products = state.get('products');
    const settings = state.get('settings');
    const stats = state.get('stats');
    
    const now = new Date();
    const logs = [];

    logs.push(`[${now.toISOString()}] [INFO] ToriBot v2 - Log Viewer Initialized`);
    logs.push(`[${now.toISOString()}] [INFO] Total products in database: ${stats.total}`);
    logs.push(`[${now.toISOString()}] [INFO] Products with AI valuation: ${stats.withValuation}`);
    logs.push(`[${now.toISOString()}] [INFO] New products today: ${stats.newToday}`);
    
    if (settings) {
      logs.push(`[${now.toISOString()}] [INFO] Poll interval: ${settings.poll_interval_seconds}s`);
      logs.push(`[${now.toISOString()}] [INFO] OpenAI enabled: ${settings.openai?.enabled}`);
    }

    if (stats.errors > 0) {
      logs.push(`[${now.toISOString()}] [WARNING] ${stats.errors} products have extraction errors`);
    }

    logs.push(`[${now.toISOString()}] [INFO] Bot status: ${state.get('botStatus')}`);
    logs.push(`[${now.toISOString()}] [INFO] Monitoring active...`);
    
    logs.push('');
    logs.push('Note: Real-time log streaming requires backend implementation.');
    logs.push('To view actual logs, check the debug/ directory in the bot folder.');

    return logs.join('\n');
  },

  /**
   * Refresh logs
   */
  async refresh() {
    toast.info('Refreshing logs...');
    await this.loadLogs();
    toast.success('Logs refreshed');
  },

  /**
   * Copy logs to clipboard
   */
  async copyLogs() {
    const viewer = document.getElementById('log-viewer');
    if (!viewer) return;
    
    const text = viewer.innerText;
    await UI.copyToClipboard(text);
  },

  /**
   * Clear logs
   */
  async clearLogs() {
    const confirmed = await UI.confirm(
      'Clear Logs',
      'Are you sure you want to clear all logs? This action cannot be undone.'
    );

    if (confirmed) {
      const viewer = document.getElementById('log-viewer');
      if (viewer) {
        viewer.innerHTML = UI.createEmptyState(
          '<i class="fas fa-file-alt"></i>',
          'Logs cleared',
          'New logs will appear here as the bot runs'
        );
      }
      toast.success('Logs cleared');
    }
  },
};
