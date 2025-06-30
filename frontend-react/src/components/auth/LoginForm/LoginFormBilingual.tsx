// Bilingual Login Form component

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Link,
  Divider,
  IconButton,
  InputAdornment,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
} from '@mui/icons-material';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../../hooks/useAuth';
import { VALIDATION } from '../../../utils/constants';
import { LanguageSwitcher } from '../../common/LanguageSwitcher';

interface LoginFormProps {
  onSuccess?: () => void;
}

export const LoginFormBilingual: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  const { login, isLoading, error, clearError } = useAuth();

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Get redirect path from location state
  const from = (location.state as any)?.from?.pathname || null;

  // Check if admin login requested
  const isAdminLogin = new URLSearchParams(location.search).get('type') === 'admin';

  // Determine redirect path based on user role
  const getRedirectPath = (userRole: string) => {
    // If there's a specific path requested, use it (unless it's role-restricted)
    if (from) {
      return from;
    }
    
    // Otherwise, redirect based on role
    switch (userRole) {
      case 'admin':
        return '/admin';
      case 'owner':
        return '/dashboard'; // Owner uses the same dashboard route
      case 'client':
      default:
        return '/dashboard';
    }
  };

  // Handle input changes
  const handleChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field error when user starts typing
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: '' }));
    }
    
    // Clear auth error when user starts typing
    if (error) {
      clearError();
    }
  };

  // Validate form
  const validateForm = () => {
    const errors: Record<string, string> = {};

    if (!formData.email) {
      errors.email = t('auth.login.errors.emailRequired', 'Email is required');
    } else if (!VALIDATION.EMAIL_REGEX.test(formData.email)) {
      errors.email = t('auth.login.errors.invalidEmail', 'Please enter a valid email address');
    }

    if (!formData.password) {
      errors.password = t('auth.login.errors.passwordRequired', 'Password is required');
    } else if (formData.password.length < VALIDATION.PASSWORD_MIN_LENGTH) {
      errors.password = t('auth.login.errors.passwordTooShort', 
        `Password must be at least ${VALIDATION.PASSWORD_MIN_LENGTH} characters`);
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    const result = await login(formData);

    if (result.success && result.user) {
      if (onSuccess) {
        onSuccess();
      } else {
        const redirectPath = getRedirectPath(result.user.role);
        navigate(redirectPath, { replace: true });
      }
    }
  };

  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  // Translate error messages from backend
  const getTranslatedError = (error: string) => {
    if (error.toLowerCase().includes('invalid') || error.toLowerCase().includes('incorrect')) {
      return t('auth.login.errors.invalidCredentials');
    }
    if (error.toLowerCase().includes('suspended') || error.toLowerCase().includes('blocked')) {
      return t('auth.login.errors.accountSuspended');
    }
    return error;
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      px={2}
      py={4}
      sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        direction: isRTL ? 'rtl' : 'ltr',
      }}
    >
      <Card
        sx={{
          maxWidth: 400,
          width: '100%',
          boxShadow: 4,
        }}
      >
        <CardContent sx={{ p: 4 }}>
          {/* Header with Language Switcher */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box />
            <LanguageSwitcher />
          </Box>
          
          {/* Title */}
          <Box textAlign="center" mb={3}>
            <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
              {t('common.appName')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {isAdminLogin ? t('auth.login.adminSubtitle', 'Admin Login') : t('auth.login.subtitle')}
            </Typography>
          </Box>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {getTranslatedError(error)}
            </Alert>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label={t('auth.login.email')}
              type="email"
              value={formData.email}
              onChange={handleChange('email')}
              error={!!formErrors.email}
              helperText={formErrors.email}
              margin="normal"
              autoComplete="email"
              autoFocus
              dir="ltr"
              InputProps={{
                startAdornment: (
                  <InputAdornment position={isRTL ? "end" : "start"}>
                    <Email color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label={t('auth.login.password')}
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleChange('password')}
              error={!!formErrors.password}
              helperText={formErrors.password}
              margin="normal"
              autoComplete="current-password"
              dir="ltr"
              InputProps={{
                startAdornment: (
                  <InputAdornment position={isRTL ? "end" : "start"}>
                    <Lock color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position={isRTL ? "start" : "end"}>
                    <IconButton
                      onClick={togglePasswordVisibility}
                      edge={isRTL ? "start" : "end"}
                      aria-label="toggle password visibility"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isLoading}
              sx={{ mt: 3, mb: 2, py: 1.5 }}
            >
              {isLoading ? t('auth.login.submitting', 'Signing In...') : t('auth.login.submit')}
            </Button>
          </form>

          {/* Divider */}
          <Divider sx={{ my: 2 }} />

          {/* Links */}
          <Box textAlign="center" display="flex" flexDirection="column" gap={1}>
            <Link
              component={RouterLink}
              to="/forgot-password"
              variant="body2"
              underline="hover"
            >
              {t('auth.login.forgotPassword')}
            </Link>
            
            <Typography variant="body2" color="text.secondary">
              {t('auth.login.noAccount')}{' '}
              <Link
                component={RouterLink}
                to="/signup"
                underline="hover"
              >
                {t('auth.login.signupLink')}
              </Link>
            </Typography>
            
            {/* Toggle between client and admin login */}
            <Link
              component={RouterLink}
              to={isAdminLogin ? "/login" : "/login?type=admin"}
              variant="body2"
              underline="hover"
              sx={{ mt: 1 }}
            >
              {isAdminLogin 
                ? t('navigation.clientLogin', 'Client Login')
                : t('navigation.adminLogin', 'Admin Login')
              }
            </Link>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};