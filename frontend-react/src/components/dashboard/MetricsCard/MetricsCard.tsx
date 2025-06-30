// Metrics card component for displaying KPIs

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';

interface TrendData {
  value: number;
  direction: 'up' | 'down' | 'flat';
}

interface MetricsCardProps {
  title: string;
  value: number | string;
  icon: React.ReactElement;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  trend?: TrendData;
  subtitle?: string;
  period?: string;
  formatValue?: (value: number | string) => string;
  onClick?: () => void;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  icon,
  color = 'primary',
  trend,
  subtitle,
  period,
  formatValue,
  onClick,
}) => {
  const theme = useTheme();

  const getColorValue = (colorName: string) => {
    switch (colorName) {
      case 'primary':
        return theme.palette.primary.main;
      case 'secondary':
        return theme.palette.secondary.main;
      case 'success':
        return theme.palette.success.main;
      case 'error':
        return theme.palette.error.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'info':
        return theme.palette.info.main;
      default:
        return theme.palette.primary.main;
    }
  };

  const colorValue = getColorValue(color);

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'up':
        return <TrendingUp fontSize="small" />;
      case 'down':
        return <TrendingDown fontSize="small" />;
      case 'flat':
      default:
        return <TrendingFlat fontSize="small" />;
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'up':
        return theme.palette.success.main;
      case 'down':
        return theme.palette.error.main;
      case 'flat':
      default:
        return theme.palette.grey[500];
    }
  };

  const displayValue = formatValue ? formatValue(value) : value.toString();

  return (
    <Card
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s ease-in-out',
        '&:hover': onClick ? {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[4],
        } : {},
        position: 'relative',
        overflow: 'visible',
      }}
      onClick={onClick}
    >
      {/* Color accent line */}
      <Box
        sx={{
          height: 4,
          backgroundColor: colorValue,
          borderRadius: '4px 4px 0 0',
        }}
      />
      
      <CardContent sx={{ pb: 2 }}>
        <Box display="flex" alignItems="flex-start" justifyContent="space-between">
          <Box flex={1}>
            <Typography
              variant="body2"
              color="text.secondary"
              gutterBottom
              sx={{ fontWeight: 500 }}
            >
              {title}
            </Typography>
            
            <Typography
              variant="h4"
              component="div"
              sx={{
                fontWeight: 'bold',
                color: 'text.primary',
                mb: 1,
              }}
            >
              {displayValue}
            </Typography>

            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}

            {trend && (
              <Box display="flex" alignItems="center" gap={0.5} mt={1}>
                <Box
                  sx={{
                    color: getTrendColor(trend.direction),
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  {getTrendIcon(trend.direction)}
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    color: getTrendColor(trend.direction),
                    fontWeight: 500,
                  }}
                >
                  {Math.abs(trend.value)}%
                </Typography>
                {period && (
                  <Typography variant="body2" color="text.secondary">
                    {period}
                  </Typography>
                )}
              </Box>
            )}
          </Box>

          <Box
            sx={{
              backgroundColor: alpha(colorValue, 0.1),
              borderRadius: 2,
              p: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minWidth: 48,
              minHeight: 48,
            }}
          >
            {React.cloneElement(icon, {
              sx: {
                fontSize: 24,
                color: colorValue,
              },
            })}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

// Skeleton loading version of MetricsCard
export const MetricsCardSkeleton: React.FC = () => {
  const theme = useTheme();
  
  return (
    <Card sx={{ height: '100%' }}>
      <Box
        sx={{
          height: 4,
          backgroundColor: theme.palette.grey[300],
          borderRadius: '4px 4px 0 0',
        }}
      />
      <CardContent>
        <Box display="flex" alignItems="flex-start" justifyContent="space-between">
          <Box flex={1}>
            <Box
              sx={{
                height: 16,
                backgroundColor: theme.palette.grey[300],
                borderRadius: 1,
                mb: 1,
                width: '70%',
              }}
            />
            <Box
              sx={{
                height: 32,
                backgroundColor: theme.palette.grey[300],
                borderRadius: 1,
                mb: 1,
                width: '90%',
              }}
            />
            <Box
              sx={{
                height: 14,
                backgroundColor: theme.palette.grey[300],
                borderRadius: 1,
                width: '60%',
              }}
            />
          </Box>
          <Box
            sx={{
              backgroundColor: theme.palette.grey[200],
              borderRadius: 2,
              width: 48,
              height: 48,
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};