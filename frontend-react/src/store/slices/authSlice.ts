// Authentication slice for Redux store

import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import { authApi } from '../../services/api/endpoints/auth';
import type { User, AuthState, LoginCredentials, RegisterData } from '../../services/api/types/auth';

// Extend AuthState with lastActivity
interface ExtendedAuthState extends AuthState {
  lastActivity: number | null;
}

// Async thunks for authentication
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials) => {
    const response = await authApi.login(credentials);
    return response;
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (data: RegisterData) => {
    const response = await authApi.register(data);
    return response;
  }
);

export const refreshAccessToken = createAsyncThunk(
  'auth/refresh',
  async (_, { getState }) => {
    const state = getState() as { auth: ExtendedAuthState };
    const refreshToken = state.auth.refreshToken;
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response = await authApi.refreshToken(refreshToken);
    return response;
  }
);

export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async () => {
    const response = await authApi.getCurrentUser();
    return response;
  }
);

const initialState: ExtendedAuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  isAuthenticated: false,
  isLoading: false,
  error: null,
  lastActivity: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{
        user: User;
        access_token: string;
        refresh_token: string;
      }>
    ) => {
      const { user, access_token, refresh_token } = action.payload;
      
      state.user = user;
      state.token = access_token;
      state.refreshToken = refresh_token;
      state.isAuthenticated = true;
      state.error = null;
      state.lastActivity = Date.now();
      
      // Store in localStorage for persistence
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));
    },
    
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      state.lastActivity = Date.now();
      localStorage.setItem('access_token', action.payload);
    },
    
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      localStorage.setItem('user', JSON.stringify(action.payload));
    },
    
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;
      state.lastActivity = null;
      
      // Clear localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    },
    
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    
    updateLastActivity: (state) => {
      state.lastActivity = Date.now();
    },
    
    initializeAuth: (state) => {
      // Initialize authentication state from localStorage
      const token = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      const userStr = localStorage.getItem('user');
      
      if (token && refreshToken && userStr) {
        try {
          const user = JSON.parse(userStr);
          state.token = token;
          state.refreshToken = refreshToken;
          state.user = user;
          state.isAuthenticated = true;
          state.lastActivity = Date.now();
        } catch (error) {
          // Invalid stored data, clear it
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
        }
      }
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        const { user, access_token, refresh_token } = action.payload;
        state.user = user;
        state.token = access_token;
        state.refreshToken = refresh_token;
        state.isAuthenticated = true;
        state.isLoading = false;
        state.error = null;
        state.lastActivity = Date.now();
        
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('user', JSON.stringify(user));
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Login failed';
      });
    
    // Register
    builder
      .addCase(register.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        const { user, access_token, refresh_token } = action.payload;
        state.user = user;
        state.token = access_token;
        state.refreshToken = refresh_token;
        state.isAuthenticated = true;
        state.isLoading = false;
        state.error = null;
        state.lastActivity = Date.now();
        
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('user', JSON.stringify(user));
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Registration failed';
      });
    
    // Refresh token
    builder
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        const { access_token } = action.payload;
        state.token = access_token;
        state.lastActivity = Date.now();
        localStorage.setItem('access_token', access_token);
      })
      .addCase(refreshAccessToken.rejected, (state) => {
        // If refresh fails, logout user
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        state.error = 'Session expired. Please login again.';
        
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      });
    
    // Fetch current user
    builder
      .addCase(fetchCurrentUser.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload;
        state.isLoading = false;
        localStorage.setItem('user', JSON.stringify(action.payload));
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.isLoading = false;
      });
  },
});

export const {
  setCredentials,
  setToken,
  setUser,
  logout,
  setLoading,
  setError,
  updateLastActivity,
  initializeAuth,
} = authSlice.actions;

export default authSlice.reducer;

// Selectors
export const selectCurrentUser = (state: { auth: ExtendedAuthState }) => state.auth.user;
export const selectToken = (state: { auth: ExtendedAuthState }) => state.auth.token;
export const selectIsAuthenticated = (state: { auth: ExtendedAuthState }) => state.auth.isAuthenticated;
export const selectAuthError = (state: { auth: ExtendedAuthState }) => state.auth.error;
export const selectAuthLoading = (state: { auth: ExtendedAuthState }) => state.auth.isLoading;