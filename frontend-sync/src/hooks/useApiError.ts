// Custom hook for handling API errors with user-friendly messages
import { useCallback } from 'react';
import { useSnackbar } from 'notistack';

interface ApiErrorDetails {
  message: string;
  code?: string;
  status?: number;
  details?: Record<string, any>;
}

export const useApiError = () => {
  const { enqueueSnackbar } = useSnackbar();

  const handleError = useCallback((error: any) => {
    let errorMessage = 'An unexpected error occurred';
    let severity: 'error' | 'warning' = 'error';

    if (error instanceof Error) {
      errorMessage = error.message;
      
      // Check for specific error properties
      const apiError = error as Error & ApiErrorDetails;
      
      // Handle specific status codes
      if (apiError.status) {
        switch (apiError.status) {
          case 401:
            errorMessage = 'Please log in to continue';
            severity = 'warning';
            break;
          case 403:
            errorMessage = 'You do not have permission to perform this action';
            break;
          case 404:
            errorMessage = 'The requested resource was not found';
            break;
          case 429:
            errorMessage = 'Too many requests. Please slow down';
            severity = 'warning';
            break;
          case 500:
          case 502:
          case 503:
            errorMessage = 'Server error. Please try again later';
            break;
        }
      }
      
      // Show validation errors if available
      if (apiError.details?.validation_errors) {
        const validationMessages = Object.entries(apiError.details.validation_errors)
          .map(([field, messages]: [string, any]) => {
            const messageList = Array.isArray(messages) ? messages : [messages];
            return `${field}: ${messageList.join(', ')}`;
          });
        
        validationMessages.forEach(msg => {
          enqueueSnackbar(msg, { variant: 'error' });
        });
        return;
      }
    }

    // Show the main error message
    enqueueSnackbar(errorMessage, { variant: severity });
  }, [enqueueSnackbar]);

  return { handleError };
};