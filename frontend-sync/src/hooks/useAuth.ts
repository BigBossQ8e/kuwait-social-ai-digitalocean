// Authentication hook for Kuwait Social AI

import { useCallback, useEffect } from 'react';
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
  
  // Selectors
  const user = useAppSelector(selectCurrentUser);
  const token = useAppSelector(selectToken);
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const isLoading = useAppSelector(selectAuthLoading);
  const error = useAppSelector(selectAuthError);
  
  // API mutations
  const [loginMutation] = useLoginMutation();
  const [logoutMutation] = useLogoutMutation();
  
  // Get current user query (only if token exists)
  const { 
    data: currentUserData, 
    error: currentUserError, 
    isLoading: isCurrentUserLoading 
  } = useGetCurrentUserQuery(undefined, {
    skip: !token,
  });

  // Initialize auth state on hook mount
  useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  // Update user data when query succeeds
  useEffect(() => {
    if (currentUserData) {
      dispatch(setCredentials({
        user: currentUserData,
        access_token: token!,
        refresh_token: localStorage.getItem('refresh_token')!,
      }));
    }
  }, [currentUserData, token, dispatch]);

  // Handle current user query error
  useEffect(() => {
    if (currentUserError) {
      // If user query fails, logout
      dispatch(logout());
    }
  }, [currentUserError, dispatch]);

  // Login function
  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      dispatch(setLoading(true));
      dispatch(setError(null));
      
      const response = await loginMutation(credentials).unwrap();
      
      dispatch(setCredentials({
        user: response.user,
        access_token: response.access_token,
        refresh_token: response.refresh_token,
      }));
      
      return { success: true, user: response.user };
    } catch (error: any) {
      const errorMessage = error?.message || 'Login failed';
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

  // Force logout (for use in error handling)
  const forceLogout = useCallback(() => {
    dispatch(logout());
  }, [dispatch]);

  // Clear auth errors
  const clearError = useCallback(() => {
    dispatch(setError(null));
  }, [dispatch]);

  return {
    // State
    user,
    token,
    isAuthenticated,
    isLoading: isLoading || isCurrentUserLoading,
    error,
    
    // Actions
    login,
    logout: logoutUser,
    forceLogout,
    clearError,
    
    // Utilities
    hasRole,
    isAdmin,
    isClient,
  };
};