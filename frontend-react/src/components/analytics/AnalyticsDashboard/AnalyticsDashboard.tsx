// Analytics dashboard with charts and metrics

import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  ButtonGroup,
  Select,
  MenuItem,
  FormControl,
  Stack,
  Chip,
  Avatar,
  useTheme,
  Skeleton,
  Alert,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
} from '@mui/material';
import Grid2 from '@mui/material/Grid2';
import {
  TrendingUp,
  Instagram,
  Twitter,
  CameraAlt,
  People,
  Favorite,
  Visibility,
  Download,
  Refresh,
  Info,
  ArrowUpward,
  ArrowDownward,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format, subDays } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import type { AnalyticsData } from '../../../types/api.types';

interface AnalyticsDashboardProps {
  data?: AnalyticsData;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
  onExport?: (format: 'csv' | 'pdf') => void;
}

type DateRange = '7days' | '30days' | '90days' | 'custom';
type MetricType = 'engagement' | 'reach' | 'impressions' | 'clicks';

const platformColors = {
  instagram: '#E4405F',
  twitter: '#1DA1F2',
  snapchat: '#FFFC00',
};

// Mock data generator
const generateMockData = (days: number) => {
  const data = [];
  const today = new Date();
  
  for (let i = days - 1; i >= 0; i--) {
    const date = subDays(today, i);
    data.push({
      date: format(date, 'MMM dd'),
      instagram: {
        impressions: Math.floor(Math.random() * 5000) + 1000,
        reach: Math.floor(Math.random() * 3000) + 500,
        engagement: Math.floor(Math.random() * 500) + 50,
        followers: Math.floor(Math.random() * 100) + 10,
      },
      twitter: {
        impressions: Math.floor(Math.random() * 3000) + 500,
        reach: Math.floor(Math.random() * 2000) + 300,
        engagement: Math.floor(Math.random() * 300) + 30,
        followers: Math.floor(Math.random() * 50) + 5,
      },
      snapchat: {
        impressions: Math.floor(Math.random() * 2000) + 300,
        reach: Math.floor(Math.random() * 1500) + 200,
        engagement: Math.floor(Math.random() * 200) + 20,
        followers: Math.floor(Math.random() * 30) + 3,
      },
    });
  }
  
  return data;
};

const MetricCard: React.FC<{
  title: string;
  value: number | string;
  change?: number;
  icon?: React.ReactNode;
  color?: string;
  loading?: boolean;
}> = ({ title, value, change, icon, color, loading }) => {
  const theme = useTheme();
  
  if (loading) {
    return (
      <Card>
        <CardContent>
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" height={40} />
          <Skeleton variant="text" width="30%" />
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography color="text.secondary" variant="body2" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </Typography>
            {change !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                {change > 0 ? (
                  <ArrowUpward fontSize="small" color="success" />
                ) : (
                  <ArrowDownward fontSize="small" color="error" />
                )}
                <Typography
                  variant="body2"
                  color={change > 0 ? 'success.main' : 'error.main'}
                >
                  {Math.abs(change)}%
                </Typography>
              </Box>
            )}
          </Box>
          {icon && (
            <Avatar
              sx={{
                backgroundColor: color || theme.palette.primary.main,
                width: 48,
                height: 48,
              }}
            >
              {icon}
            </Avatar>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  loading = false,
  error = null,
  onRefresh,
  onExport,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const locale = language === 'ar' ? ar : enUS;
  
  const [dateRange, setDateRange] = useState<DateRange>('7days');
  const [selectedPlatform, setSelectedPlatform] = useState<'all' | 'instagram' | 'twitter' | 'snapchat'>('all');
  const [selectedMetric, setSelectedMetric] = useState<MetricType>('engagement');
  
  // Generate mock data based on date range
  const chartData = useMemo(() => {
    const days = dateRange === '7days' ? 7 : dateRange === '30days' ? 30 : 90;
    return generateMockData(days);
  }, [dateRange]);
  
  // Calculate totals
  const totals = useMemo(() => {
    const result = {
      impressions: 0,
      reach: 0,
      engagement: 0,
      followers: 0,
    };
    
    chartData.forEach(day => {
      Object.values(day).forEach(platform => {
        if (typeof platform === 'object') {
          result.impressions += platform.impressions || 0;
          result.reach += platform.reach || 0;
          result.engagement += platform.engagement || 0;
          result.followers += platform.followers || 0;
        }
      });
    });
    
    return result;
  }, [chartData]);
  
  // Platform distribution data
  const platformDistribution = useMemo(() => {
    const distribution = {
      instagram: 0,
      twitter: 0,
      snapchat: 0,
    };
    
    chartData.forEach(day => {
      distribution.instagram += day.instagram?.engagement || 0;
      distribution.twitter += day.twitter?.engagement || 0;
      distribution.snapchat += day.snapchat?.engagement || 0;
    });
    
    return Object.entries(distribution).map(([platform, value]) => ({
      name: platform,
      value,
      color: platformColors[platform as keyof typeof platformColors],
    }));
  }, [chartData]);
  
  // Top performing posts mock data
  const topPosts = [
    {
      id: 1,
      caption: 'Exciting Kuwait National Day celebrations! 🇰🇼',
      platform: 'instagram',
      engagement: 1234,
      date: new Date(),
    },
    {
      id: 2,
      caption: 'New product launch announcement #KuwaitBusiness',
      platform: 'twitter',
      engagement: 987,
      date: subDays(new Date(), 2),
    },
    {
      id: 3,
      caption: 'Behind the scenes at our Kuwait office',
      platform: 'snapchat',
      engagement: 654,
      date: subDays(new Date(), 5),
    },
  ];
  
  const handleDateRangeChange = (range: DateRange) => {
    setDateRange(range);
  };
  
  const renderEngagementChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={chartData}>
        <defs>
          <linearGradient id="instagramGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={platformColors.instagram} stopOpacity={0.8}/>
            <stop offset="95%" stopColor={platformColors.instagram} stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="twitterGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={platformColors.twitter} stopOpacity={0.8}/>
            <stop offset="95%" stopColor={platformColors.twitter} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <RechartsTooltip />
        <Legend />
        {(selectedPlatform === 'all' || selectedPlatform === 'instagram') && (
          <Area
            type="monotone"
            dataKey="instagram.engagement"
            stroke={platformColors.instagram}
            fillOpacity={1}
            fill="url(#instagramGradient)"
            name="Instagram"
          />
        )}
        {(selectedPlatform === 'all' || selectedPlatform === 'twitter') && (
          <Area
            type="monotone"
            dataKey="twitter.engagement"
            stroke={platformColors.twitter}
            fillOpacity={1}
            fill="url(#twitterGradient)"
            name="Twitter"
          />
        )}
      </AreaChart>
    </ResponsiveContainer>
  );
  
  const renderMetricsChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <RechartsTooltip />
        <Legend />
        {(selectedPlatform === 'all' || selectedPlatform === 'instagram') && (
          <Line
            type="monotone"
            dataKey={`instagram.${selectedMetric}`}
            stroke={platformColors.instagram}
            name="Instagram"
            strokeWidth={2}
          />
        )}
        {(selectedPlatform === 'all' || selectedPlatform === 'twitter') && (
          <Line
            type="monotone"
            dataKey={`twitter.${selectedMetric}`}
            stroke={platformColors.twitter}
            name="Twitter"
            strokeWidth={2}
          />
        )}
        {(selectedPlatform === 'all' || selectedPlatform === 'snapchat') && (
          <Line
            type="monotone"
            dataKey={`snapchat.${selectedMetric}`}
            stroke={platformColors.snapchat}
            name="Snapchat"
            strokeWidth={2}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
  
  const renderPlatformDistribution = () => (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={platformDistribution}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {platformDistribution.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <RechartsTooltip />
      </PieChart>
    </ResponsiveContainer>
  );
  
  if (error) {
    return (
      <Alert severity="error" action={
        onRefresh && (
          <Button color="inherit" size="small" onClick={onRefresh}>
            {language === 'ar' ? 'إعادة المحاولة' : 'Retry'}
          </Button>
        )
      }>
        {error}
      </Alert>
    );
  }
  
  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          {language === 'ar' ? 'لوحة التحليلات' : 'Analytics Dashboard'}
        </Typography>
        
        <Stack direction="row" spacing={2}>
          {/* Date Range Selector */}
          <ButtonGroup size="small">
            <Button
              variant={dateRange === '7days' ? 'contained' : 'outlined'}
              onClick={() => handleDateRangeChange('7days')}
            >
              {language === 'ar' ? '٧ أيام' : '7 Days'}
            </Button>
            <Button
              variant={dateRange === '30days' ? 'contained' : 'outlined'}
              onClick={() => handleDateRangeChange('30days')}
            >
              {language === 'ar' ? '٣٠ يوم' : '30 Days'}
            </Button>
            <Button
              variant={dateRange === '90days' ? 'contained' : 'outlined'}
              onClick={() => handleDateRangeChange('90days')}
            >
              {language === 'ar' ? '٩٠ يوم' : '90 Days'}
            </Button>
          </ButtonGroup>
          
          {/* Actions */}
          {onRefresh && (
            <IconButton onClick={onRefresh} disabled={loading}>
              <Refresh />
            </IconButton>
          )}
          {onExport && (
            <Button
              startIcon={<Download />}
              onClick={() => onExport('csv')}
              disabled={loading}
            >
              {language === 'ar' ? 'تصدير' : 'Export'}
            </Button>
          )}
        </Stack>
      </Box>
      
      {/* Summary Cards */}
      <Grid2 container spacing={3} mb={3}>
        <Grid2 size={{ xs: 12, sm: 6, md: 3 }}>
          <MetricCard
            title={language === 'ar' ? 'إجمالي الانطباعات' : 'Total Impressions'}
            value={totals.impressions}
            change={12}
            icon={<Visibility />}
            color={theme.palette.info.main}
            loading={loading}
          />
        </Grid2>
        <Grid2 size={{ xs: 12, sm: 6, md: 3 }}>
          <MetricCard
            title={language === 'ar' ? 'الوصول' : 'Reach'}
            value={totals.reach}
            change={8}
            icon={<TrendingUp />}
            color={theme.palette.success.main}
            loading={loading}
          />
        </Grid2>
        <Grid2 size={{ xs: 12, sm: 6, md: 3 }}>
          <MetricCard
            title={language === 'ar' ? 'التفاعل' : 'Engagement'}
            value={totals.engagement}
            change={-5}
            icon={<Favorite />}
            color={theme.palette.error.main}
            loading={loading}
          />
        </Grid2>
        <Grid2 size={{ xs: 12, sm: 6, md: 3 }}>
          <MetricCard
            title={language === 'ar' ? 'المتابعون الجدد' : 'New Followers'}
            value={totals.followers}
            change={15}
            icon={<People />}
            color={theme.palette.warning.main}
            loading={loading}
          />
        </Grid2>
      </Grid2>
      
      {/* Charts */}
      <Grid2 container spacing={3}>
        {/* Engagement Trend */}
        <Grid2 size={{ xs: 12, lg: 8 }}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                {language === 'ar' ? 'اتجاه التفاعل' : 'Engagement Trend'}
              </Typography>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <Select
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value as 'all' | 'instagram' | 'twitter' | 'snapchat')}
                >
                  <MenuItem value="all">
                    {language === 'ar' ? 'الكل' : 'All'}
                  </MenuItem>
                  <MenuItem value="instagram">Instagram</MenuItem>
                  <MenuItem value="twitter">Twitter</MenuItem>
                  <MenuItem value="snapchat">Snapchat</MenuItem>
                </Select>
              </FormControl>
            </Box>
            {loading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : (
              renderEngagementChart()
            )}
          </Paper>
        </Grid2>
        
        {/* Platform Distribution */}
        <Grid2 size={{ xs: 12, lg: 4 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'توزيع المنصات' : 'Platform Distribution'}
            </Typography>
            {loading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : (
              renderPlatformDistribution()
            )}
          </Paper>
        </Grid2>
        
        {/* Metrics Comparison */}
        <Grid2 size={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                {language === 'ar' ? 'مقارنة المقاييس' : 'Metrics Comparison'}
              </Typography>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <Select
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value as MetricType)}
                >
                  <MenuItem value="engagement">
                    {language === 'ar' ? 'التفاعل' : 'Engagement'}
                  </MenuItem>
                  <MenuItem value="reach">
                    {language === 'ar' ? 'الوصول' : 'Reach'}
                  </MenuItem>
                  <MenuItem value="impressions">
                    {language === 'ar' ? 'الانطباعات' : 'Impressions'}
                  </MenuItem>
                  <MenuItem value="clicks">
                    {language === 'ar' ? 'النقرات' : 'Clicks'}
                  </MenuItem>
                </Select>
              </FormControl>
            </Box>
            {loading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : (
              renderMetricsChart()
            )}
          </Paper>
        </Grid2>
        
        {/* Top Performing Posts */}
        <Grid2 size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'أفضل المنشورات أداءً' : 'Top Performing Posts'}
            </Typography>
            <List>
              {topPosts.map((post, index) => (
                <React.Fragment key={post.id}>
                  <ListItem alignItems="flex-start">
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: platformColors[post.platform as keyof typeof platformColors] }}>
                        {post.platform === 'instagram' && <Instagram />}
                        {post.platform === 'twitter' && <Twitter />}
                        {post.platform === 'snapchat' && <CameraAlt />}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={post.caption}
                      secondary={
                        <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                          <Chip
                            size="small"
                            icon={<Favorite fontSize="small" />}
                            label={post.engagement.toLocaleString()}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {format(post.date, 'PPP', { locale })}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < topPosts.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid2>
        
        {/* Best Posting Times */}
        <Grid2 size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'أفضل أوقات النشر' : 'Best Posting Times'}
            </Typography>
            <Alert severity="info" icon={<Info />} sx={{ mb: 2 }}>
              {language === 'ar' 
                ? 'بناءً على تحليل جمهورك في الكويت'
                : 'Based on your Kuwait audience analysis'
              }
            </Alert>
            <Stack spacing={2}>
              {[
                { day: language === 'ar' ? 'الأحد - الخميس' : 'Sunday - Thursday', times: '6:00 PM - 9:00 PM' },
                { day: language === 'ar' ? 'الجمعة' : 'Friday', times: '1:00 PM - 3:00 PM, 8:00 PM - 11:00 PM' },
                { day: language === 'ar' ? 'السبت' : 'Saturday', times: '5:00 PM - 10:00 PM' },
              ].map((schedule, index) => (
                <Box key={index} display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" fontWeight="medium">
                    {schedule.day}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {schedule.times}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Paper>
        </Grid2>
      </Grid2>
    </Box>
  );
};