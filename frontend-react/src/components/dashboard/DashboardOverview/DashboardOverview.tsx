// Dashboard overview component - main dashboard page

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  useTheme,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  TrendingUp,
  PostAdd,
  Visibility,
  ThumbUp,
  Schedule,
  Analytics,
} from '@mui/icons-material';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { MetricsCard } from '../MetricsCard';
import { RecentActivity } from '../RecentActivity';
import { PrayerTimeWidget } from '../../features/PrayerTimeWidget';
import { PageLoading } from '../../common/LoadingSpinner';

// Mock data - will be replaced with real API calls
const mockMetrics = {
  totalPosts: 156,
  totalViews: 45230,
  totalLikes: 3420,
  engagementRate: 7.8,
  scheduledPosts: 12,
  pendingPosts: 3,
};

const mockRecentActivity = [
  {
    id: '1',
    type: 'post_published',
    title: 'New product launch announcement',
    description: 'Instagram post published successfully',
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    platform: 'instagram',
  },
  {
    id: '2',
    type: 'engagement',
    title: 'High engagement detected',
    description: 'Your latest post is performing 40% above average',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    platform: 'instagram',
  },
  {
    id: '3',
    type: 'schedule',
    title: 'Posts scheduled',
    description: '5 posts scheduled for this week',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6), // 6 hours ago
    platform: 'multiple',
  },
  {
    id: '4',
    type: 'competitor',
    title: 'Competitor analysis complete',
    description: 'Weekly competitor report is ready',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    platform: 'analysis',
  },
];

export const DashboardOverview: React.FC = () => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  
  // Mock loading state - replace with actual loading state from API
  const isLoading = false;

  if (isLoading) {
    return <PageLoading message={language === 'ar' ? 'جارٍ تحميل البيانات...' : 'Loading dashboard data...'} />;
  }

  return (
    <Box>
      {/* Page Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          {language === 'ar' ? 'لوحة التحكم' : 'Dashboard'}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {language === 'ar' 
            ? 'نظرة عامة على أداء حساباتك على وسائل التواصل الاجتماعي'
            : 'Overview of your social media performance'
          }
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Metrics Cards Row */}
        <Grid xs={12}>
          <Grid container spacing={3}>
            <Grid xs={12} sm={6} md={4}>
              <MetricsCard
                title={language === 'ar' ? 'إجمالي المنشورات' : 'Total Posts'}
                value={mockMetrics.totalPosts}
                icon={<PostAdd />}
                color="primary"
                trend={{ value: 12, direction: 'up' }}
                period={language === 'ar' ? 'هذا الشهر' : 'This month'}
              />
            </Grid>
            <Grid xs={12} sm={6} md={4}>
              <MetricsCard
                title={language === 'ar' ? 'إجمالي المشاهدات' : 'Total Views'}
                value={mockMetrics.totalViews}
                icon={<Visibility />}
                color="info"
                trend={{ value: 8.5, direction: 'up' }}
                period={language === 'ar' ? 'هذا الشهر' : 'This month'}
                formatValue={(value) => value.toLocaleString()}
              />
            </Grid>
            <Grid xs={12} sm={6} md={4}>
              <MetricsCard
                title={language === 'ar' ? 'إجمالي الإعجابات' : 'Total Likes'}
                value={mockMetrics.totalLikes}
                icon={<ThumbUp />}
                color="success"
                trend={{ value: 15.2, direction: 'up' }}
                period={language === 'ar' ? 'هذا الشهر' : 'This month'}
                formatValue={(value) => value.toLocaleString()}
              />
            </Grid>
            <Grid xs={12} sm={6} md={4}>
              <MetricsCard
                title={language === 'ar' ? 'معدل التفاعل' : 'Engagement Rate'}
                value={mockMetrics.engagementRate}
                icon={<TrendingUp />}
                color="warning"
                trend={{ value: 2.1, direction: 'up' }}
                period={language === 'ar' ? 'هذا الشهر' : 'This month'}
                formatValue={(value) => `${value}%`}
              />
            </Grid>
            <Grid xs={12} sm={6} md={4}>
              <MetricsCard
                title={language === 'ar' ? 'المنشورات المجدولة' : 'Scheduled Posts'}
                value={mockMetrics.scheduledPosts}
                icon={<Schedule />}
                color="secondary"
                subtitle={language === 'ar' ? 'هذا الأسبوع' : 'This week'}
              />
            </Grid>
            <Grid xs={12} sm={6} md={4}>
              <MetricsCard
                title={language === 'ar' ? 'المنشورات المعلقة' : 'Pending Posts'}
                value={mockMetrics.pendingPosts}
                icon={<Analytics />}
                color="error"
                subtitle={language === 'ar' ? 'تتطلب مراجعة' : 'Require review'}
              />
            </Grid>
          </Grid>
        </Grid>

        {/* Second Row - Activity Feed and Prayer Times */}
        <Grid xs={12} lg={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'النشاط الأخير' : 'Recent Activity'}
            </Typography>
            <RecentActivity activities={mockRecentActivity} />
          </Paper>
        </Grid>

        <Grid xs={12} lg={4}>
          <PrayerTimeWidget />
        </Grid>

        {/* Third Row - Performance Chart Placeholder */}
        <Grid xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'أداء المحتوى' : 'Content Performance'}
            </Typography>
            <Box
              sx={{
                height: 300,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: theme.palette.grey[50],
                borderRadius: 1,
                border: `2px dashed ${theme.palette.grey[300]}`,
              }}
            >
              <Box textAlign="center">
                <Analytics sx={{ fontSize: 48, color: theme.palette.grey[400], mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  {language === 'ar' ? 'قريباً' : 'Coming Soon'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {language === 'ar' 
                    ? 'مخطط أداء المحتوى التفاعلي'
                    : 'Interactive content performance chart'
                  }
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};