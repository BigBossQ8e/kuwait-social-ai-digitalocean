// Enhanced Authentication hook with timeout handling
import { useCallback, useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { 
  setCredentials, 
  logout, 
  setLoading, 
  setError, 
  initializeAuth,
  selectCurrentUser,
  selectToken,
  selectIsAuthenticated,
  selectAuthLoading,
  selectAuthError
} from '../store/slices/authSlice';
import { 
  useLoginMutation, 
  useLogoutMutation, 
  useGetCurrentUserQuery 
} from '../services/api/auth';
import type { LoginCredentials } from '../types/api.types';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const [skipUserQuery, setSkipUserQuery] = useState(false);
  
  // Selectors
  const user = useAppSelector(selectCurrentUser);
  const token = useAppSelector(selectToken);
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const isLoading = useAppSelector(selectAuthLoading);
  const error = useAppSelector(selectAuthError);
  
  // API mutations
  const [loginMutation] = useLoginMutation();
  const [logoutMutation] = useLogoutMutation();
  
  // Get current user query (only if token exists and not skipped)
  const { 
    data: currentUserData, 
    error: currentUserError, 
    isLoading: isCurrentUserLoading,
    refetch: refetchUser
  } = useGetCurrentUserQuery(undefined, {
    skip: !token || skipUserQuery,
    // Add polling interval to retry failed requests
    pollingInterval: 0, // Disable automatic polling
    refetchOnMountOrArgChange: true,
    refetchOnReconnect: true,
  });

  // Initialize auth state on hook mount
  useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  // Add timeout for user query
  useEffect(() => {
    if (isCurrentUserLoading && token) {
      const timer = setTimeout(() => {
        console.warn('User verification timeout - skipping query');
        setSkipUserQuery(true);
        dispatch(setLoading(false));
        
        // If we have a user in localStorage, keep them authenticated
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          try {
            const parsedUser = JSON.parse(storedUser);
            if (parsedUser && parsedUser.id) {
              // User exists in storage, continue with cached data
              dispatch(setError(null));
              return;
            }
          } catch (e) {
            console.error('Failed to parse stored user:', e);
          }
        }
        
        // No valid user in storage, show error
        dispatch(setError('Unable to verify authentication. Please try logging in again.'));
      }, 8000); // 8 second timeout

      return () => clearTimeout(timer);
    }
  }, [isCurrentUserLoading, token, dispatch]);

  // Update user data when query succeeds
  useEffect(() => {
    if (currentUserData) {
      dispatch(setCredentials({
        user: currentUserData,
        access_token: token!,
        refresh_token: localStorage.getItem('refresh_token')!,
      }));
      setSkipUserQuery(false); // Reset skip flag on success
    }
  }, [currentUserData, token, dispatch]);

  // Handle current user query error
  useEffect(() => {
    if (currentUserError) {
      console.error('User query error:', currentUserError);
      
      // Check if we have cached user data
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        try {
          const parsedUser = JSON.parse(storedUser);
          if (parsedUser && parsedUser.id && token) {
            // Use cached user data if available
            console.log('Using cached user data due to API error');
            dispatch(setCredentials({
              user: parsedUser,
              access_token: token,
              refresh_token: localStorage.getItem('refresh_token')!,
            }));
            setSkipUserQuery(true); // Skip further queries
            return;
          }
        } catch (e) {
          console.error('Failed to use cached user data:', e);
        }
      }
      
      // If no cached data or invalid, logout
      dispatch(logout());
    }
  }, [currentUserError, token, dispatch]);

  // Login function
  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      dispatch(setLoading(true));
      dispatch(setError(null));
      setSkipUserQuery(false); // Reset skip flag on new login
      
      const response = await loginMutation(credentials).unwrap();
      
      dispatch(setCredentials({
        user: response.user,
        access_token: response.access_token,
        refresh_token: response.refresh_token,
      }));
      
      // Store user in localStorage for fallback
      localStorage.setItem('user', JSON.stringify(response.user));
      
      return { success: true, user: response.user };
    } catch (error: any) {
      const errorMessage = error?.data?.message || error?.message || 'Login failed';
      dispatch(setError(errorMessage));
      return { success: false, error: errorMessage };
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch, loginMutation]);

  // Logout function
  const logoutUser = useCallback(async () => {
    try {
      // Call logout API endpoint
      await logoutMutation().unwrap();
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error);
    } finally {
      // Always clear local state
      dispatch(logout());
      setSkipUserQuery(false); // Reset skip flag
    }
  }, [dispatch, logoutMutation]);

  // Check if user has specific role
  const hasRole = useCallback((role: string) => {
    return user?.role === role;
  }, [user]);

  // Check if user is admin
  const isAdmin = useCallback(() => {
    return hasRole('admin');
  }, [hasRole]);

  // Check if user is client
  const isClient = useCallback(() => {
    return hasRole('client');
  }, [hasRole]);

  // Check if user is owner
  const isOwner = useCallback(() => {
    return hasRole('owner');
  }, [hasRole]);

  // Force logout (for use in error handling)
  const forceLogout = useCallback(() => {
    dispatch(logout());
    setSkipUserQuery(false);
  }, [dispatch]);

  // Clear auth errors
  const clearError = useCallback(() => {
    dispatch(setError(null));
  }, [dispatch]);

  // Retry user verification
  const retryUserVerification = useCallback(() => {
    setSkipUserQuery(false);
    dispatch(setError(null));
    if (token) {
      refetchUser();
    }
  }, [dispatch, token, refetchUser]);

  return {
    // State
    user,
    token,
    isAuthenticated,
    isLoading: isLoading || (isCurrentUserLoading && !skipUserQuery),
    error,
    
    // Actions
    login,
    logout: logoutUser,
    forceLogout,
    clearError,
    retryUserVerification,
    
    // Utilities
    hasRole,
    isAdmin,
    isClient,
    isOwner,
  };
};