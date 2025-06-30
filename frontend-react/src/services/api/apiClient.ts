// Centralized API client for Kuwait Social AI
import axios, { type AxiosInstance, type AxiosError, type AxiosRequestConfig } from 'axios';
import { store } from '../../store';
import { logout, refreshAccessToken } from '../../store/slices/authSlice';

// Define API error structure
interface ApiError {
  error: string;
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const state = store.getState();
    const token = state.auth.token;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    }
    return response;
  },
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // Log error in development
    if (import.meta.env.DEV) {
      console.error(`❌ ${originalRequest.method?.toUpperCase()} ${originalRequest.url}`, error.response?.data);
    }
    
    // Handle 401 Unauthorized - attempt token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const state = store.getState();
        const refreshToken = state.auth.refreshToken;
        
        if (refreshToken) {
          // Attempt to refresh token
          const result = await store.dispatch(refreshAccessToken()).unwrap();
          
          if (result.access_token) {
            // Retry original request with new token
            return apiClient(originalRequest);
          }
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        store.dispatch(logout());
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // Handle other errors
    if (error.response) {
      // Server responded with error
      const apiError = error.response.data;
      const errorMessage = apiError?.message || apiError?.error || 'An error occurred';
      
      // Create enhanced error object
      const enhancedError = new Error(errorMessage) as Error & {
        code?: string;
        details?: Record<string, any>;
        status?: number;
      };
      
      enhancedError.code = apiError?.code;
      enhancedError.details = apiError?.details;
      enhancedError.status = error.response.status;
      
      // Handle specific error codes
      switch (error.response.status) {
        case 400:
          // Bad request - show validation errors
          if (apiError?.details?.validation_errors) {
            enhancedError.message = formatValidationErrors(apiError.details.validation_errors);
          }
          break;
          
        case 403:
          // Forbidden - insufficient permissions
          enhancedError.message = 'You do not have permission to perform this action';
          break;
          
        case 404:
          // Not found
          enhancedError.message = 'The requested resource was not found';
          break;
          
        case 429:
          // Rate limited
          enhancedError.message = 'Too many requests. Please try again later';
          break;
          
        case 500:
          // Server error
          enhancedError.message = 'Server error. Please try again later';
          break;
      }
      
      return Promise.reject(enhancedError);
    } else if (error.request) {
      // Request made but no response received
      const networkError = new Error('Network error. Please check your connection');
      return Promise.reject(networkError);
    } else {
      // Something else happened
      return Promise.reject(error);
    }
  }
);

// Helper function to format validation errors
function formatValidationErrors(errors: Record<string, string[]>): string {
  const messages = Object.entries(errors)
    .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
    .join('; ');
  return `Validation failed: ${messages}`;
}

// Convenience methods for common requests
export const api = {
  // GET request
  get: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<T>(url, config).then(res => res.data),
  
  // POST request
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.post<T>(url, data, config).then(res => res.data),
  
  // PUT request
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.put<T>(url, data, config).then(res => res.data),
  
  // PATCH request
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.patch<T>(url, data, config).then(res => res.data),
  
  // DELETE request
  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<T>(url, config).then(res => res.data),
  
  // File upload with progress
  uploadFile: <T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void,
    additionalData?: Record<string, any>
  ) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add additional data if provided
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }
    
    return apiClient.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    }).then(res => res.data);
  },
};

// Export types
export type { ApiError };

// Export the raw axios instance for advanced use cases
export { apiClient };

export default api;