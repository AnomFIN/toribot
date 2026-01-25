// ==========================================================================
// ToriBot v2 - Internationalization (i18n) Service
// Language management and translations
// ==========================================================================

const i18n = {
  currentLang: 'fi', // Default to Finnish
  
  translations: {
    fi: {
      // Sidebar & Navigation
      'sidebar.title': 'ToriBot v2',
      'nav.dashboard': 'Kojelauta',
      'nav.products': 'Tuotteet',
      'nav.logs': 'Lokit',
      'nav.settings': 'Asetukset',
      'theme.dark': 'Tumma tila',
      'theme.light': 'Valoisa tila',
      
      // Header
      'header.search': 'Etsi tuotteita...',
      'status.checking': 'Tarkistetaan...',
      'status.online': 'Verkossa',
      'status.offline': 'Ei yhteyttä',
      
      // Dashboard
      'dashboard.title': 'Kojelauta',
      'dashboard.description': 'Tori.fi seurantabotin yleiskatsaus',
      'dashboard.stats.total': 'Tuotteita yhteensä',
      'dashboard.stats.newToday': 'Uusia tänään',
      'dashboard.stats.withValuation': 'Arvioituja',
      'dashboard.stats.errors': 'Virheitä',
      'dashboard.quickActions': 'Pikatoiminnot',
      'dashboard.fetchProducts': 'Hae uusia tuotteita',
      'dashboard.runValuation': 'Suorita AI-arviointi',
      'dashboard.refreshAll': 'Päivitä kaikki tuotteet',
      'dashboard.exportCSV': 'Vie CSV-tiedostoon',
      'dashboard.recentProducts': 'Viimeisimmät tuotteet',
      'dashboard.viewAll': 'Näytä kaikki',
      'dashboard.noProducts': 'Ei tuotteita vielä',
      'dashboard.noProductsDesc': 'Aloita hakemalla tuotteita Tori.fi-palvelusta',
      
      // Products
      'products.title': 'Tuotteet',
      'products.description': 'Selaa ja hallinnoi löydettyjä tuotteita',
      'products.filter.search': 'Haku',
      'products.filter.location': 'Sijainti',
      'products.filter.dateFrom': 'Alkaen',
      'products.filter.hasValuation': 'Arvioitu',
      'products.filter.all': 'Kaikki',
      'products.filter.yes': 'Kyllä',
      'products.filter.no': 'Ei',
      'products.filter.apply': 'Suodata',
      'products.filter.clear': 'Tyhjennä',
      'products.viewGrid': 'Ruudukkonäkymä',
      'products.viewTable': 'Taulukkonäkymä',
      'products.noFound': 'Tuotteita ei löytynyt',
      'products.noFoundDesc': 'Kokeile muuttaa suodattimia tai hae uusia tuotteita',
      'products.table.title': 'Otsikko',
      'products.table.location': 'Sijainti',
      'products.table.price': 'Hinta',
      'products.table.worth': 'Arvo',
      'products.table.discovered': 'Löydetty',
      'products.table.status': 'Tila',
      'products.table.actions': 'Toiminnot',
      'products.valuated': 'Arvioitu',
      'products.viewDetails': 'Näytä tiedot',
      'products.openTori': 'Avaa Tori.fi:ssä',
      
      // Product Detail
      'product.location': 'Sijainti',
      'product.seller': 'Myyjä',
      'product.discovered': 'Löydetty',
      'product.price': 'Hinta',
      'product.worth': 'Arvo',
      'product.valuation': 'AI-arviointi',
      'product.noValuation': 'Ei arviointia vielä',
      'product.noDescription': 'Ei kuvausta',
      'product.noImages': 'Ei kuvia saatavilla',
      'product.close': 'Sulje',
      'product.viewOnTori': 'Näytä Tori.fi:ssä',
      'product.notFound': 'Tuotetta ei löytynyt',
      
      // Settings
      'settings.title': 'Asetukset',
      'settings.description': 'Määritä botin asetukset',
      'settings.general': 'Yleiset asetukset',
      'settings.pollInterval': 'Hakuväli (sekuntia)',
      'settings.requestTimeout': 'Pyynnön aikakatkaisu (sekuntia)',
      'settings.maxRetries': 'Uudelleenyrityksiä',
      'settings.productsPerPage': 'Tuotteita per sivu',
      'settings.openai': 'OpenAI-asetukset',
      'settings.openai.enabled': 'OpenAI käytössä',
      'settings.openai.apiKey': 'API-avain',
      'settings.openai.model': 'Malli',
      'settings.openai.valuationInterval': 'Arviointiväli (min)',
      'settings.images': 'Kuvien lataus',
      'settings.images.enabled': 'Lataa kuvat',
      'settings.images.maxPerItem': 'Kuvia enintään',
      'settings.save': 'Tallenna asetukset',
      'settings.cancel': 'Peruuta',
      'settings.saved': 'Asetukset tallennettu',
      'settings.error': 'Virhe tallennettaessa asetuksia',
      
      // Logs
      'logs.title': 'Lokit',
      'logs.description': 'Näytä botin aktiviteettilokit',
      'logs.clear': 'Tyhjennä lokit',
      'logs.download': 'Lataa lokit',
      'logs.filter.all': 'Kaikki',
      'logs.filter.info': 'Info',
      'logs.filter.warning': 'Varoitus',
      'logs.filter.error': 'Virhe',
      'logs.empty': 'Ei lokeja',
      'logs.emptyDesc': 'Lokit näkyvät tässä, kun bot on aktiivinen',
      
      // Common
      'common.loading': 'Ladataan...',
      'common.error': 'Virhe',
      'common.success': 'Onnistui',
      'common.na': 'Ei saatavilla',
      'common.free': 'Ilmainen',
      'common.refresh': 'Päivitä',
      'common.save': 'Tallenna',
      'common.cancel': 'Peruuta',
      'common.delete': 'Poista',
      'common.edit': 'Muokkaa',
      'common.view': 'Näytä',
      'common.close': 'Sulje',
      'common.yes': 'Kyllä',
      'common.no': 'Ei',
      'common.maybe': 'Ehkä',
      
      // Toast messages
      'toast.fetchingProducts': 'Haetaan tuotteita...',
      'toast.productsFetched': 'Tuotteet haettu onnistuneesti',
      'toast.fetchError': 'Virhe haettaessa tuotteita',
      'toast.runningValuation': 'Suoritetaan AI-arviointia...',
      'toast.valuationStarted': 'Arviointi aloitettu',
      'toast.valuationError': 'Virhe käynnistettäessä arviointia',
      'toast.refreshing': 'Päivitetään tietoja...',
      'toast.refreshed': 'Tiedot päivitetty',
      'toast.exporting': 'Viedään tuotteita...',
      'toast.exported': 'Tallennettu {{count}} tuotetta tiedostoon {{filename}}',
      'toast.exportError': 'Virhe vietäessä tuotteita',
      'toast.settingsSaved': 'Asetukset tallennettu',
      'toast.settingsError': 'Virhe tallennettaessa asetuksia',
      'toast.themeChanged': 'Teema vaihdettu {{theme}}-tilaan',
    },
    
    en: {
      // Sidebar & Navigation
      'sidebar.title': 'ToriBot v2',
      'nav.dashboard': 'Dashboard',
      'nav.products': 'Products',
      'nav.logs': 'Logs',
      'nav.settings': 'Settings',
      'theme.dark': 'Dark Mode',
      'theme.light': 'Light Mode',
      
      // Header
      'header.search': 'Search products...',
      'status.checking': 'Checking...',
      'status.online': 'Online',
      'status.offline': 'Offline',
      
      // Dashboard
      'dashboard.title': 'Dashboard',
      'dashboard.description': 'Overview of your Tori.fi monitoring bot',
      'dashboard.stats.total': 'Total Products',
      'dashboard.stats.newToday': 'New Today',
      'dashboard.stats.withValuation': 'AI Valuated',
      'dashboard.stats.errors': 'Errors',
      'dashboard.quickActions': 'Quick Actions',
      'dashboard.fetchProducts': 'Fetch New Products',
      'dashboard.runValuation': 'Run AI Valuation',
      'dashboard.refreshAll': 'Refresh All Products',
      'dashboard.exportCSV': 'Export to CSV',
      'dashboard.recentProducts': 'Recent Products',
      'dashboard.viewAll': 'View All',
      'dashboard.noProducts': 'No products yet',
      'dashboard.noProductsDesc': 'Start by fetching products from Tori.fi',
      
      // Products
      'products.title': 'Products',
      'products.description': 'Browse and manage discovered products',
      'products.filter.search': 'Search',
      'products.filter.location': 'Location',
      'products.filter.dateFrom': 'Date From',
      'products.filter.hasValuation': 'Has Valuation',
      'products.filter.all': 'All',
      'products.filter.yes': 'Yes',
      'products.filter.no': 'No',
      'products.filter.apply': 'Apply Filters',
      'products.filter.clear': 'Clear',
      'products.viewGrid': 'Grid view',
      'products.viewTable': 'Table view',
      'products.noFound': 'No products found',
      'products.noFoundDesc': 'Try adjusting your filters or fetch new products',
      'products.table.title': 'Title',
      'products.table.location': 'Location',
      'products.table.price': 'Price',
      'products.table.worth': 'Worth',
      'products.table.discovered': 'Discovered',
      'products.table.status': 'Status',
      'products.table.actions': 'Actions',
      'products.valuated': 'Valuated',
      'products.viewDetails': 'View details',
      'products.openTori': 'Open on Tori.fi',
      
      // Product Detail
      'product.location': 'Location',
      'product.seller': 'Seller',
      'product.discovered': 'Discovered',
      'product.price': 'Price',
      'product.worth': 'Worth',
      'product.valuation': 'AI Valuation',
      'product.noValuation': 'No AI valuation yet',
      'product.noDescription': 'No description',
      'product.noImages': 'No images available',
      'product.close': 'Close',
      'product.viewOnTori': 'View on Tori.fi',
      'product.notFound': 'Product not found',
      
      // Settings
      'settings.title': 'Settings',
      'settings.description': 'Configure bot settings',
      'settings.general': 'General Settings',
      'settings.pollInterval': 'Poll Interval (seconds)',
      'settings.requestTimeout': 'Request Timeout (seconds)',
      'settings.maxRetries': 'Max Retries',
      'settings.productsPerPage': 'Products Per Page',
      'settings.openai': 'OpenAI Settings',
      'settings.openai.enabled': 'OpenAI Enabled',
      'settings.openai.apiKey': 'API Key',
      'settings.openai.model': 'Model',
      'settings.openai.valuationInterval': 'Valuation Interval (min)',
      'settings.images': 'Image Download',
      'settings.images.enabled': 'Download Images',
      'settings.images.maxPerItem': 'Max Images Per Item',
      'settings.save': 'Save Settings',
      'settings.cancel': 'Cancel',
      'settings.saved': 'Settings saved',
      'settings.error': 'Error saving settings',
      
      // Logs
      'logs.title': 'Logs',
      'logs.description': 'View bot activity logs',
      'logs.clear': 'Clear Logs',
      'logs.download': 'Download Logs',
      'logs.filter.all': 'All',
      'logs.filter.info': 'Info',
      'logs.filter.warning': 'Warning',
      'logs.filter.error': 'Error',
      'logs.empty': 'No logs',
      'logs.emptyDesc': 'Logs will appear here when the bot is active',
      
      // Common
      'common.loading': 'Loading...',
      'common.error': 'Error',
      'common.success': 'Success',
      'common.na': 'N/A',
      'common.free': 'Free',
      'common.refresh': 'Refresh',
      'common.save': 'Save',
      'common.cancel': 'Cancel',
      'common.delete': 'Delete',
      'common.edit': 'Edit',
      'common.view': 'View',
      'common.close': 'Close',
      'common.yes': 'Yes',
      'common.no': 'No',
      'common.maybe': 'Maybe',
      
      // Toast messages
      'toast.fetchingProducts': 'Fetching products...',
      'toast.productsFetched': 'Products fetched successfully',
      'toast.fetchError': 'Failed to fetch products',
      'toast.runningValuation': 'Running AI valuation...',
      'toast.valuationStarted': 'Valuation started',
      'toast.valuationError': 'Failed to trigger valuation',
      'toast.refreshing': 'Refreshing data...',
      'toast.refreshed': 'Data refreshed',
      'toast.exporting': 'Exporting products...',
      'toast.exported': 'Saved {{count}} products to {{filename}}',
      'toast.exportError': 'Failed to export products',
      'toast.settingsSaved': 'Settings saved',
      'toast.settingsError': 'Error saving settings',
      'toast.themeChanged': 'Theme switched to {{theme}} mode',
    }
  },
  
  /**
   * Initialize i18n system
   */
  init() {
    // Load saved language preference or default to Finnish
    const savedLang = localStorage.getItem('language');
    this.currentLang = (savedLang && this.translations[savedLang]) ? savedLang : 'fi';
    
    console.log(`🌐 i18n initialized with language: ${this.currentLang}`);
  },
  
  /**
   * Get translation for a key
   */
  t(key, params = {}) {
    const translation = this.translations[this.currentLang]?.[key] || key;
    
    // Replace parameters in translation (e.g., {{count}})
    return translation.replace(/\{\{(\w+)\}\}/g, (match, param) => {
      return params[param] !== undefined ? params[param] : match;
    });
  },
  
  /**
   * Set current language
   */
  setLanguage(lang) {
    if (!this.translations[lang]) {
      console.error(`Language '${lang}' not found`);
      return false;
    }
    
    this.currentLang = lang;
    localStorage.setItem('language', lang);
    console.log(`Language changed to: ${lang}`);
    
    // Trigger language change event
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    
    return true;
  },
  
  /**
   * Get current language
   */
  getLanguage() {
    return this.currentLang;
  },
  
  /**
   * Get available languages
   */
  getAvailableLanguages() {
    return Object.keys(this.translations);
  }
};

// Initialize on load
i18n.init();
