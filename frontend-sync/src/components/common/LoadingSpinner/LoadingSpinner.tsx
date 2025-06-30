// Loading spinner component with different variants

import React from 'react';
import {
  Box,
  CircularProgress,
  LinearProgress,
  Typography,
  Backdrop,
  Card,
  CardContent,
} from '@mui/material';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';

interface LoadingSpinnerProps {
  variant?: 'circular' | 'linear' | 'backdrop' | 'card';
  size?: 'small' | 'medium' | 'large';
  message?: string;
  overlay?: boolean;
  color?: 'primary' | 'secondary' | 'inherit';
}

const sizeMap = {
  small: 24,
  medium: 40,
  large: 60,
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  variant = 'circular',
  size = 'medium',
  message,
  overlay = false,
  color = 'primary',
}) => {
  const language = useAppSelector(selectLanguage);
  
  const defaultMessage = language === 'ar' ? 'جارٍ التحميل...' : 'Loading...';
  const displayMessage = message || defaultMessage;

  const renderSpinner = () => {
    switch (variant) {
      case 'linear':
        return (
          <Box sx={{ width: '100%' }}>
            <LinearProgress color={color} />
            {message && (
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ mt: 1, textAlign: 'center' }}
              >
                {displayMessage}
              </Typography>
            )}
          </Box>
        );

      case 'backdrop':
        return (
          <Backdrop
            open={true}
            sx={{ 
              color: '#fff', 
              zIndex: (theme) => theme.zIndex.drawer + 1,
              backgroundColor: 'rgba(0, 0, 0, 0.7)',
            }}
          >
            <Box 
              display="flex" 
              flexDirection="column" 
              alignItems="center" 
              gap={2}
            >
              <CircularProgress color="inherit" size={sizeMap[size]} />
              <Typography variant="body1" color="inherit">
                {displayMessage}
              </Typography>
            </Box>
          </Backdrop>
        );

      case 'card':
        return (
          <Card sx={{ maxWidth: 300, mx: 'auto' }}>
            <CardContent>
              <Box 
                display="flex" 
                flexDirection="column" 
                alignItems="center" 
                gap={2}
                py={2}
              >
                <CircularProgress color={color} size={sizeMap[size]} />
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  {displayMessage}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        );

      case 'circular':
      default:
        return (
          <Box 
            display="flex" 
            flexDirection="column" 
            alignItems="center" 
            gap={message ? 2 : 0}
          >
            <CircularProgress color={color} size={sizeMap[size]} />
            {message && (
              <Typography 
                variant="body2" 
                color="text.secondary"
                textAlign="center"
              >
                {displayMessage}
              </Typography>
            )}
          </Box>
        );
    }
  };

  if (overlay && variant !== 'backdrop') {
    return (
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          zIndex: 1,
        }}
      >
        {renderSpinner()}
      </Box>
    );
  }

  return renderSpinner();
};

// Page-level loading component
export const PageLoading: React.FC<{ message?: string }> = ({ message }) => {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="50vh"
    >
      <LoadingSpinner variant="card" size="large" message={message} />
    </Box>
  );
};

// Inline loading component for smaller sections
export const InlineLoading: React.FC<{ message?: string }> = ({ message }) => {
  return (
    <Box display="flex" justifyContent="center" py={3}>
      <LoadingSpinner size="small" message={message} />
    </Box>
  );
};