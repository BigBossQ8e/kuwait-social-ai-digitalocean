import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  useTheme,
  Divider,
  Alert,
} from '@mui/material';
import {
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Payment as PaymentIcon,
  Group as GroupIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { MetricsCard } from '../dashboard/MetricsCard';
import { useAppDispatch, useAppSelector } from '../../store';
import { selectCurrentUser } from '../../store/slices/authSlice';
import { api } from '../../services/api';

interface OwnerStats {
  businessName: string;
  subscriptionPlan: string;
  subscriptionStatus: 'active' | 'trial' | 'expired';
  daysUntilRenewal: number;
  totalPosts: number;
  scheduledPosts: number;
  publishedToday: number;
  engagementRate: number;
  teamMembers: number;
  platformsConnected: string[];
  recentActivity: Array<{
    id: string;
    type: 'post_published' | 'post_scheduled' | 'team_joined' | 'platform_connected';
    description: string;
    timestamp: string;
  }>;
}

export const OwnerDashboard: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const user = useAppSelector(selectCurrentUser);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<OwnerStats>({
    businessName: '',
    subscriptionPlan: 'Basic',
    subscriptionStatus: 'active',
    daysUntilRenewal: 30,
    totalPosts: 0,
    scheduledPosts: 0,
    publishedToday: 0,
    engagementRate: 0,
    teamMembers: 1,
    platformsConnected: [],
    recentActivity: [],
  });

  const fetchOwnerStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/owner/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching owner stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOwnerStats();
  }, []);

  const getSubscriptionColor = (status: string) => {
    switch (status) {
      case 'active':
        return theme.palette.success.main;
      case 'trial':
        return theme.palette.warning.main;
      case 'expired':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'post_published':
        return <CheckCircleIcon color="success" />;
      case 'post_scheduled':
        return <ScheduleIcon color="primary" />;
      case 'team_joined':
        return <GroupIcon color="info" />;
      case 'platform_connected':
        return <BusinessIcon color="secondary" />;
      default:
        return <BusinessIcon />;
    }
  };

  if (loading) return <LinearProgress />;

  return (
    <Box>
      <Box mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Welcome back, {user?.name || 'Business Owner'}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          {stats.businessName || 'Your Business'}
        </Typography>
      </Box>

      {/* Subscription Alert */}
      {stats.subscriptionStatus === 'trial' && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Your trial ends in {stats.daysUntilRenewal} days. Upgrade now to continue using all features.
          <Button size="small" sx={{ ml: 2 }}>
            Upgrade Plan
          </Button>
        </Alert>
      )}

      {/* Key Metrics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Total Posts"
            value={stats.totalPosts}
            trend={15}
            icon={<BusinessIcon />}
            color={theme.palette.primary.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Scheduled"
            value={stats.scheduledPosts}
            icon={<ScheduleIcon />}
            color={theme.palette.info.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Published Today"
            value={stats.publishedToday}
            trend={25}
            icon={<TrendingUpIcon />}
            color={theme.palette.success.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Engagement Rate"
            value={`${stats.engagementRate}%`}
            trend={8}
            icon={<AnalyticsIcon />}
            color={theme.palette.warning.main}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Subscription & Billing */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Subscription" />
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Current Plan
                  </Typography>
                  <Typography variant="h6">{stats.subscriptionPlan}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={stats.subscriptionStatus}
                    color={
                      stats.subscriptionStatus === 'active'
                        ? 'success'
                        : stats.subscriptionStatus === 'trial'
                        ? 'warning'
                        : 'error'
                    }
                    size="small"
                  />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Renewal
                  </Typography>
                  <Typography variant="body1">
                    {stats.daysUntilRenewal} days remaining
                  </Typography>
                </Box>
                <Divider />
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<PaymentIcon />}
                  color="primary"
                >
                  Manage Subscription
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Connected Platforms */}
          <Card sx={{ mt: 3 }}>
            <CardHeader title="Connected Platforms" />
            <CardContent>
              <Box display="flex" flexDirection="column" gap={1}>
                {stats.platformsConnected.length > 0 ? (
                  stats.platformsConnected.map((platform) => (
                    <Chip
                      key={platform}
                      label={platform}
                      variant="outlined"
                      size="small"
                      color="primary"
                    />
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No platforms connected yet
                  </Typography>
                )}
              </Box>
              <Button variant="outlined" fullWidth sx={{ mt: 2 }}>
                Connect Platform
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Quick Actions" />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    fullWidth
                    size="large"
                    startIcon={<BusinessIcon />}
                  >
                    Create New Post
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <Button variant="outlined" fullWidth startIcon={<ScheduleIcon />}>
                    Schedule Posts
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <Button variant="outlined" fullWidth startIcon={<AnalyticsIcon />}>
                    View Analytics
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <Button variant="outlined" fullWidth startIcon={<GroupIcon />}>
                    Manage Team
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <Button variant="outlined" fullWidth startIcon={<SettingsIcon />}>
                    Business Settings
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Recent Activity" />
            <CardContent>
              <List>
                {stats.recentActivity.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem alignItems="flex-start">
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'background.default' }}>
                          {getActivityIcon(activity.type)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={activity.description}
                        secondary={new Date(activity.timestamp).toLocaleString()}
                      />
                    </ListItem>
                    {index < stats.recentActivity.length - 1 && <Divider variant="inset" component="li" />}
                  </React.Fragment>
                ))}
              </List>
              {stats.recentActivity.length === 0 && (
                <Typography variant="body2" color="text.secondary" align="center">
                  No recent activity
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};