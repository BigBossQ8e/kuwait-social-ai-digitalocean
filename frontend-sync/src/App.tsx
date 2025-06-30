// Main App component for Kuwait Social AI

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import rtlPlugin from 'stylis-plugin-rtl';
import { CssBaseline, Box } from '@mui/material';
import { store } from './store';
import { LoginForm } from './components/auth/LoginForm';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppLayout } from './components/common/Layout';
import { DashboardOverview } from './components/dashboard/DashboardOverview';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { useAppSelector } from './store';
import { selectTheme, selectDirection } from './store/slices/uiSlice';

// Create RTL cache for Arabic support
const rtlCache = createCache({
  key: 'muirtl',
  stylisPlugins: [rtlPlugin],
});

const ltrCache = createCache({
  key: 'muiltr',
});

// Theme configuration
const createAppTheme = (mode: 'light' | 'dark', direction: 'ltr' | 'rtl') => {
  return createTheme({
    palette: {
      mode,
      primary: {
        main: '#1976d2',
        light: '#42a5f5',
        dark: '#1565c0',
      },
      secondary: {
        main: '#dc004e',
        light: '#ff6b9d',
        dark: '#9a0036',
      },
      background: {
        default: mode === 'light' ? '#f5f5f5' : '#121212',
        paper: mode === 'light' ? '#ffffff' : '#1e1e1e',
      },
    },
    direction,
    typography: {
      fontFamily: direction === 'rtl' 
        ? 'Noto Kufi Arabic, Arial, sans-serif'
        : 'Roboto, Arial, sans-serif',
      h1: {
        fontWeight: 700,
      },
      h2: {
        fontWeight: 600,
      },
      h3: {
        fontWeight: 600,
      },
    },
    shape: {
      borderRadius: 8,
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          },
        },
      },
    },
  });
};

// App content component (needs to be inside Provider to access store)
const AppContent: React.FC = () => {
  const theme = useAppSelector(selectTheme);
  const direction = useAppSelector(selectDirection);
  
  const appTheme = createAppTheme(theme === 'auto' ? 'light' : theme, direction);
  const cache = direction === 'rtl' ? rtlCache : ltrCache;

  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={appTheme}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginForm />} />
              
              {/* Protected routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute requiredRole="client">
                    <ErrorBoundary>
                      <AppLayout>
                        <DashboardOverview />
                      </AppLayout>
                    </ErrorBoundary>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/admin"
                element={
                  <ProtectedRoute requiredRole="admin">
                    <ErrorBoundary>
                      <AppLayout>
                        <Box p={3}>
                          <h1>Admin Panel - Coming Soon</h1>
                          <p>The admin panel will be implemented in the next phase.</p>
                        </Box>
                      </AppLayout>
                    </ErrorBoundary>
                  </ProtectedRoute>
                }
              />
              
              {/* Additional routes for other sections */}
              <Route
                path="/posts"
                element={
                  <ProtectedRoute requiredRole="client">
                    <ErrorBoundary>
                      <AppLayout>
                        <Box p={3}>
                          <h1>Posts Management - Coming Soon</h1>
                          <p>Post creation and management will be implemented in Phase 3.</p>
                        </Box>
                      </AppLayout>
                    </ErrorBoundary>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/analytics"
                element={
                  <ProtectedRoute requiredRole="client">
                    <ErrorBoundary>
                      <AppLayout>
                        <Box p={3}>
                          <h1>Analytics - Coming Soon</h1>
                          <p>Analytics dashboard will be implemented in Phase 3.</p>
                        </Box>
                      </AppLayout>
                    </ErrorBoundary>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/competitors"
                element={
                  <ProtectedRoute requiredRole="client">
                    <ErrorBoundary>
                      <AppLayout>
                        <Box p={3}>
                          <h1>Competitors - Coming Soon</h1>
                          <p>Competitor analysis will be implemented in Phase 4.</p>
                        </Box>
                      </AppLayout>
                    </ErrorBoundary>
                  </ProtectedRoute>
                }
              />
              
              {/* Redirect root to dashboard */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              {/* Catch all route */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Box>
        </Router>
      </ThemeProvider>
    </CacheProvider>
  );
};

// Main App component
const App: React.FC = () => {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
};

export default App;
