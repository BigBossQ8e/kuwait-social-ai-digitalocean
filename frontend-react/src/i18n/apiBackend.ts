import type { BackendModule, ReadCallback } from 'i18next';
import { apiClient } from '../services/api/apiClient';

interface ApiBackendOptions {
  loadPath: string;
  cacheDuration?: number;
}

class ApiBackend implements BackendModule {
  type = 'backend' as const;
  
  private options: ApiBackendOptions;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  
  constructor(services: any, options: ApiBackendOptions) {
    this.init(services, options);
  }
  
  init(services: any, options: ApiBackendOptions) {
    this.options = {
      loadPath: '/translations',
      cacheDuration: 5 * 60 * 1000, // 5 minutes default cache
      ...options
    };
  }
  
  read(language: string, namespace: string, callback: ReadCallback) {
    const cacheKey = `${language}-${namespace}`;
    const cached = this.cache.get(cacheKey);
    
    // Check cache
    if (cached && Date.now() - cached.timestamp < (this.options.cacheDuration || 0)) {
      callback(null, cached.data);
      return;
    }
    
    // Fetch from API
    apiClient
      .get(this.options.loadPath, {
        params: { locale: language }
      })
      .then(response => {
        const data = response.data;
        
        // Cache the result
        this.cache.set(cacheKey, {
          data,
          timestamp: Date.now()
        });
        
        callback(null, data);
      })
      .catch(error => {
        console.error('Failed to load translations:', error);
        
        // Try to use cached data even if expired
        if (cached) {
          callback(null, cached.data);
        } else {
          callback(error, null);
        }
      });
  }
  
  // Optional: implement save method for creating new translations
  create(languages: string[], namespace: string, key: string, fallbackValue: string) {
    // This could be implemented to automatically create missing translations
    console.log('Missing translation:', { languages, namespace, key, fallbackValue });
  }
  
  // Clear cache method
  clearCache() {
    this.cache.clear();
  }
  
  // Update cache after saving translations
  updateCache(language: string, namespace: string, data: any) {
    const cacheKey = `${language}-${namespace}`;
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now()
    });
  }
}

export default ApiBackend;