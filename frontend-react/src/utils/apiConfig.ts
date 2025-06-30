// API configuration utilities
export const getApiUrl = (): string => {
  // Use environment variable if set
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Default to relative path (works for same-domain deployments)
  return '/api';
};

export const getWebSocketUrl = (): string => {
  const apiUrl = getApiUrl();
  
  // If API URL is relative, construct WebSocket URL based on current location
  if (apiUrl.startsWith('/')) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}${apiUrl}/ws`;
  }
  
  // If API URL is absolute, replace http with ws
  return apiUrl.replace(/^http/, 'ws') + '/ws';
};

export const isProduction = (): boolean => {
  return import.meta.env.PROD;
};

export const isDevelopment = (): boolean => {
  return import.meta.env.DEV;
};

// Environment-specific configurations
export const config = {
  api: {
    baseURL: getApiUrl(),
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
  },
  auth: {
    tokenRefreshThreshold: 5 * 60 * 1000, // 5 minutes before expiry
    sessionTimeout: 30 * 60 * 1000, // 30 minutes of inactivity
  },
  upload: {
    maxFileSize: 16 * 1024 * 1024, // 16MB
    allowedImageTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    allowedVideoTypes: ['video/mp4', 'video/quicktime', 'video/x-msvideo'],
  },
  features: {
    enableAnalytics: isProduction(),
    enableErrorReporting: isProduction(),
    enableDebugMode: isDevelopment(),
  },
};