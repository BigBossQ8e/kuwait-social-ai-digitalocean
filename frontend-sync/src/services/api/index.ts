// Central API export file
export { default as apiClient } from './apiClient';
export * from './apiClient';

// Export all API endpoints
export * from './endpoints/auth';
export * from './endpoints/posts';
export * from './endpoints/analytics';

// Export all types
export * from './types/auth';
export * from './types/posts';
export * from './types/analytics';

// Re-export commonly used functions for convenience
import { authApi } from './endpoints/auth';
import { postsApi } from './endpoints/posts';
import { analyticsApi } from './endpoints/analytics';

export const api = {
  auth: authApi,
  posts: postsApi,
  analytics: analyticsApi,
};