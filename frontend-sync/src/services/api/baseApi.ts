// Base API configuration with RTK Query for Kuwait Social AI

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BaseQueryFn } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../../store/index';

// Get API base URL from environment variable or use relative path
// In production, VITE_API_URL should be set to the full API URL
// For DigitalOcean App Platform with unified routing, use relative path '/api'
const getApiBaseUrl = () => {
  // If VITE_API_URL is set, use it (for separate frontend/backend deployments)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // For unified routing on same domain (recommended for DigitalOcean App Platform)
  // This works when both frontend and backend are deployed in the same app
  return '/api';
};

// Custom base query with token handling and error processing
const baseQueryWithAuth: BaseQueryFn = async (args, api, extraOptions) => {
  const baseQuery = fetchBaseQuery({
    baseUrl: getApiBaseUrl(),
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      
      headers.set('Content-Type', 'application/json');
      headers.set('Accept', 'application/json');
      
      return headers;
    },
  });

  const result = await baseQuery(args, api, extraOptions);

  // Handle token refresh logic
  if (result.error && result.error.status === 401) {
    // Try to refresh token
    const refreshToken = (api.getState() as RootState).auth.refreshToken;
    
    if (refreshToken) {
      const refreshResult = await baseQuery(
        {
          url: '/auth/refresh',
          method: 'POST',
          body: { refresh_token: refreshToken },
        },
        api,
        extraOptions
      );

      if (refreshResult.data) {
        // Store new token and retry original request
        const { access_token } = refreshResult.data as { access_token: string };
        
        api.dispatch({ type: 'auth/setToken', payload: access_token });
        
        // Retry the original request with new token
        const retryResult = await baseQuery(args, api, extraOptions);
        return retryResult;
      } else {
        // Refresh failed, logout user
        api.dispatch({ type: 'auth/logout' });
        window.location.href = '/login';
      }
    }
  }

  return result;
};


export const api = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithAuth,
  tagTypes: [
    'User',
    'Client', 
    'Post', 
    'Analytics', 
    'Competitor', 
    'Campaign',
    'Template',
    'PrayerTimes',
    'Holidays'
  ],
  endpoints: () => ({}),
});

export default api;