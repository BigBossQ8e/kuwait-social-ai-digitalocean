// Competitor analysis dashboard with detailed insights

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  Avatar,
  Button,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  LinearProgress,
  Stack,
  Divider,
  IconButton,
  Tooltip,
  Alert,
  useTheme,
  alpha,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  TrendingUp,
  TrendingDown,
  Instagram,
  Twitter,
  CameraAlt,
  People,
  Favorite,
  ChatBubble,
  Share,
  Schedule,
  Tag,
  Assessment,
  CompareArrows,
  Speed,
  EmojiEvents,
  LocalFireDepartment,
  Timer,
  CalendarMonth,
  Info,
  Refresh,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import type { Competitor, CompetitorAnalysis } from '../../../types/api.types';

interface CompetitorAnalysisDashboardProps {
  competitor: Competitor;
  analysis?: CompetitorAnalysis;
  loading?: boolean;
  onRefresh?: () => void;
  onCompare?: (competitorId: number) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`competitor-tabpanel-${index}`}
      aria-labelledby={`competitor-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const platformColors: Record<string, string> = {
  instagram: '#E4405F',
  twitter: '#1DA1F2',
  snapchat: '#FFFC00',
};

// Mock data generators
const generateGrowthData = () => {
  const data = [];
  for (let i = 30; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    data.push({
      date: format(date, 'MMM dd'),
      followers: Math.floor(5000 + Math.random() * 1000 + i * 50),
      engagement: Number((3 + Math.random() * 2).toFixed(2)),
    });
  }
  return data;
};

const generatePostingPatternData = () => {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const hours = Array.from({ length: 24 }, (_, i) => i);
  const data: any[] = [];
  
  days.forEach((day, dayIndex) => {
    hours.forEach(hour => {
      data.push({
        day: dayIndex,
        hour,
        value: Math.floor(Math.random() * 10),
      });
    });
  });
  
  return data;
};

const generateContentPerformance = () => [
  { type: 'Photos', posts: 45, avgEngagement: 4.5 },
  { type: 'Videos', posts: 30, avgEngagement: 6.2 },
  { type: 'Reels', posts: 20, avgEngagement: 8.1 },
  { type: 'Stories', posts: 5, avgEngagement: 3.2 },
];

const generateRadarData = () => [
  { metric: 'Followers', value: 75, fullMark: 100 },
  { metric: 'Engagement', value: 85, fullMark: 100 },
  { metric: 'Consistency', value: 60, fullMark: 100 },
  { metric: 'Growth', value: 70, fullMark: 100 },
  { metric: 'Content Quality', value: 90, fullMark: 100 },
  { metric: 'Response Time', value: 40, fullMark: 100 },
];

export const CompetitorAnalysisDashboard: React.FC<CompetitorAnalysisDashboardProps> = ({
  competitor,
  analysis,
  loading = false,
  onRefresh,
  onCompare,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const locale = language === 'ar' ? ar : enUS;
  const [activeTab, setActiveTab] = useState(0);

  const growthData = generateGrowthData();
  const postingPatternData = generatePostingPatternData();
  const contentPerformance = generateContentPerformance();
  const radarData = generateRadarData();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getEngagementStatus = (rate: number) => {
    if (rate >= 5) return { label: 'Excellent', color: 'success' };
    if (rate >= 3) return { label: 'Good', color: 'info' };
    if (rate >= 1) return { label: 'Average', color: 'warning' };
    return { label: 'Poor', color: 'error' };
  };

  const renderOverview = () => (
    <Grid container spacing={3}>
      {/* Key Metrics */}
      <Grid xs={12}>
        <Grid container spacing={2}>
          <Grid xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      {language === 'ar' ? 'المتابعون' : 'Followers'}
                    </Typography>
                    <Typography variant="h4">
                      {analysis?.followers_count?.toLocaleString() || '0'}
                    </Typography>
                    <Box display="flex" alignItems="center" gap={0.5} mt={1}>
                      <TrendingUp fontSize="small" color="success" />
                      <Typography variant="body2" color="success.main">
                        +12.5%
                      </Typography>
                    </Box>
                  </Box>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1) }}>
                    <People color="primary" />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      {language === 'ar' ? 'معدل التفاعل' : 'Engagement Rate'}
                    </Typography>
                    <Typography variant="h4">
                      {analysis?.engagement_rate?.toFixed(2) || '0'}%
                    </Typography>
                    <Chip
                      size="small"
                      label={getEngagementStatus(analysis?.engagement_rate || 0).label}
                      color={getEngagementStatus(analysis?.engagement_rate || 0).color as any}
                      sx={{ mt: 1 }}
                    />
                  </Box>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.success.main, 0.1) }}>
                    <Favorite color="success" />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      {language === 'ar' ? 'المنشورات' : 'Posts'}
                    </Typography>
                    <Typography variant="h4">
                      {analysis?.posts_count || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {language === 'ar' ? '5.2 منشور/أسبوع' : '5.2 posts/week'}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.info.main, 0.1) }}>
                    <Assessment color="info" />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      {language === 'ar' ? 'متوسط الإعجابات' : 'Avg. Likes'}
                    </Typography>
                    <Typography variant="h4">
                      {analysis?.avg_likes_per_post?.toLocaleString() || '0'}
                    </Typography>
                    <Box display="flex" alignItems="center" gap={0.5} mt={1}>
                      <TrendingDown fontSize="small" color="error" />
                      <Typography variant="body2" color="error.main">
                        -5.3%
                      </Typography>
                    </Box>
                  </Box>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.warning.main, 0.1) }}>
                    <LocalFireDepartment color="warning" />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Grid>

      {/* Growth Chart */}
      <Grid xs={12} lg={8}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {language === 'ar' ? 'نمو المتابعين والتفاعل' : 'Followers & Engagement Growth'}
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={growthData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <RechartsTooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="followers"
                stroke={theme.palette.primary.main}
                name={language === 'ar' ? 'المتابعون' : 'Followers'}
                strokeWidth={2}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="engagement"
                stroke={theme.palette.success.main}
                name={language === 'ar' ? 'معدل التفاعل %' : 'Engagement Rate %'}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Top Content Themes */}
      <Grid xs={12} lg={4}>
        <Paper sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom>
            {language === 'ar' ? 'مواضيع المحتوى الرئيسية' : 'Top Content Themes'}
          </Typography>
          <List>
            {(analysis?.content_themes || ['Fashion', 'Lifestyle', 'Food', 'Travel']).map((theme, index) => (
              <ListItem key={index} disablePadding sx={{ mb: 1 }}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: alpha(platformColors[competitor.platform], 0.1), width: 32, height: 32 }}>
                    <Tag fontSize="small" sx={{ color: platformColors[competitor.platform] }} />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={theme}
                  secondary={
                    <LinearProgress
                      variant="determinate"
                      value={80 - index * 15}
                      sx={{
                        mt: 1,
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: platformColors[competitor.platform],
                        },
                      }}
                    />
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderEngagement = () => (
    <Grid container spacing={3}>
      {/* Engagement Breakdown */}
      <Grid xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {language === 'ar' ? 'تفصيل التفاعل' : 'Engagement Breakdown'}
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={contentPerformance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" />
              <YAxis />
              <RechartsTooltip />
              <Bar dataKey="avgEngagement" fill={platformColors[competitor.platform]} />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Performance Radar */}
      <Grid xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {language === 'ar' ? 'مقاييس الأداء' : 'Performance Metrics'}
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar
                name={competitor.name}
                dataKey="value"
                stroke={platformColors[competitor.platform]}
                fill={platformColors[competitor.platform]}
                fillOpacity={0.6}
              />
            </RadarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Best Performing Posts */}
      <Grid xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {language === 'ar' ? 'أفضل المنشورات أداءً' : 'Best Performing Posts'}
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            {language === 'ar' 
              ? 'تحليل محتوى المنافس يساعد في فهم ما يناسب جمهورك'
              : 'Analyzing competitor content helps understand what resonates with your audience'
            }
          </Alert>
          <List>
            {[1, 2, 3].map((post) => (
              <ListItem key={post} alignItems="flex-start" divider>
                <ListItemAvatar>
                  <Avatar
                    variant="rounded"
                    sx={{ width: 60, height: 60, bgcolor: theme.palette.grey[200] }}
                  >
                    <Instagram />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" noWrap sx={{ maxWidth: '70%' }}>
                        {language === 'ar' 
                          ? `منشور رقم ${post} - محتوى عن الموضة والأناقة`
                          : `Post ${post} - Fashion and style content`
                        }
                      </Typography>
                      <Chip
                        size="small"
                        icon={<Favorite fontSize="small" />}
                        label={`${(1000 + post * 500).toLocaleString()}`}
                      />
                    </Box>
                  }
                  secondary={
                    <Box mt={1}>
                      <Stack direction="row" spacing={2}>
                        <Typography variant="caption" color="text.secondary">
                          <ChatBubble fontSize="small" sx={{ fontSize: 14, mr: 0.5 }} />
                          {(50 + post * 20).toLocaleString()}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          <Share fontSize="small" sx={{ fontSize: 14, mr: 0.5 }} />
                          {(20 + post * 10).toLocaleString()}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {language === 'ar' ? `منذ ${post} أيام` : `${post} days ago`}
                        </Typography>
                      </Stack>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderPostingPatterns = () => (
    <Grid container spacing={3}>
      {/* Posting Frequency */}
      <Grid xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {language === 'ar' ? 'أوقات النشر' : 'Posting Times'}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {language === 'ar' 
              ? 'الأوقات الأكثر نشاطًا للمنافس (بتوقيت الكويت)'
              : "Competitor's most active posting times (Kuwait time)"
            }
          </Typography>
          
          {/* Heatmap visualization would go here */}
          <Box mt={3}>
            <Grid container spacing={1}>
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, dayIndex) => (
                <Grid xs={12} key={day}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography variant="caption" sx={{ width: 40 }}>
                      {language === 'ar' 
                        ? ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'][dayIndex]
                        : day
                      }
                    </Typography>
                    {Array.from({ length: 24 }, (_, hour) => {
                      const intensity = Math.random();
                      return (
                        <Tooltip key={hour} title={`${hour}:00 - ${hour + 1}:00`}>
                          <Box
                            sx={{
                              width: 20,
                              height: 20,
                              backgroundColor: alpha(
                                platformColors[competitor.platform],
                                intensity
                              ),
                              border: `1px solid ${theme.palette.divider}`,
                              cursor: 'pointer',
                            }}
                          />
                        </Tooltip>
                      );
                    })}
                  </Box>
                </Grid>
              ))}
            </Grid>
            <Box display="flex" justifyContent="center" alignItems="center" gap={2} mt={2}>
              <Typography variant="caption" color="text.secondary">
                {language === 'ar' ? 'أقل نشاطًا' : 'Less active'}
              </Typography>
              <Box display="flex" gap={0.5}>
                {[0.2, 0.4, 0.6, 0.8, 1].map((intensity) => (
                  <Box
                    key={intensity}
                    sx={{
                      width: 20,
                      height: 20,
                      backgroundColor: alpha(platformColors[competitor.platform], intensity),
                      border: `1px solid ${theme.palette.divider}`,
                    }}
                  />
                ))}
              </Box>
              <Typography variant="caption" color="text.secondary">
                {language === 'ar' ? 'أكثر نشاطًا' : 'More active'}
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Grid>

      {/* Best Times to Post */}
      <Grid xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {language === 'ar' ? 'أفضل أوقات النشر' : 'Best Posting Times'}
          </Typography>
          <List>
            {(analysis?.best_posting_times || ['18:00-20:00', '21:00-23:00', '13:00-15:00']).map((time, index) => (
              <ListItem key={index}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.success.main, 0.1) }}>
                    <Timer color="success" />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={time}
                  secondary={
                    index === 0 
                      ? (language === 'ar' ? 'أعلى تفاعل' : 'Highest engagement')
                      : (language === 'ar' ? 'تفاعل جيد' : 'Good engagement')
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>

      {/* Posting Consistency */}
      <Grid xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {language === 'ar' ? 'انتظام النشر' : 'Posting Consistency'}
          </Typography>
          <Box>
            <Box display="flex" justifyContent="space-between" mb={2}>
              <Typography variant="body2">
                {language === 'ar' ? 'المنشورات/اليوم' : 'Posts/Day'}
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                1.5
              </Typography>
            </Box>
            <Box display="flex" justifyContent="space-between" mb={2}>
              <Typography variant="body2">
                {language === 'ar' ? 'المنشورات/الأسبوع' : 'Posts/Week'}
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                10.5
              </Typography>
            </Box>
            <Box display="flex" justifyContent="space-between" mb={2}>
              <Typography variant="body2">
                {language === 'ar' ? 'أطول فترة توقف' : 'Longest gap'}
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {language === 'ar' ? '3 أيام' : '3 days'}
              </Typography>
            </Box>
            <Divider sx={{ my: 2 }} />
            <Alert severity="success">
              {language === 'ar' 
                ? 'المنافس ينشر بانتظام عالي'
                : 'Competitor posts very consistently'
              }
            </Alert>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderHashtags = () => (
    <Grid container spacing={3}>
      {/* Top Hashtags */}
      <Grid xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {language === 'ar' ? 'الهاشتاقات الأكثر استخدامًا' : 'Most Used Hashtags'}
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1} mt={2}>
            {(analysis?.top_hashtags || ['#Kuwait', '#Q8', '#Fashion', '#Lifestyle', '#Food', '#Travel', '#Photography', '#Art']).map((tag, index) => (
              <Chip
                key={index}
                label={tag}
                size={index < 3 ? 'medium' : 'small'}
                icon={<Tag />}
                sx={{
                  backgroundColor: alpha(platformColors[competitor.platform], 0.1),
                  color: platformColors[competitor.platform],
                  fontWeight: index < 3 ? 'bold' : 'normal',
                }}
              />
            ))}
          </Box>
          
          <Box mt={3}>
            <Typography variant="subtitle2" gutterBottom>
              {language === 'ar' ? 'استراتيجية الهاشتاق' : 'Hashtag Strategy'}
            </Typography>
            <Grid container spacing={2}>
              <Grid xs={12} sm={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h4" color="primary">
                      {analysis?.top_hashtags?.length || 15}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {language === 'ar' ? 'متوسط الهاشتاقات/منشور' : 'Avg hashtags/post'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid xs={12} sm={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h4" color="success.main">
                      65%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {language === 'ar' ? 'هاشتاقات محلية' : 'Local hashtags'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid xs={12} sm={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h4" color="info.main">
                      35%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {language === 'ar' ? 'هاشتاقات عالمية' : 'Global hashtags'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );

  return (
    <Box>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar
              sx={{
                width: 56,
                height: 56,
                bgcolor: alpha(platformColors[competitor.platform], 0.1),
              }}
            >
              {platformColors[competitor.platform] === platformColors.instagram && <Instagram />}
              {platformColors[competitor.platform] === platformColors.twitter && <Twitter />}
              {platformColors[competitor.platform] === platformColors.snapchat && <CameraAlt />}
            </Avatar>
            <Box>
              <Typography variant="h5">{competitor.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                @{competitor.username} • {competitor.platform}
              </Typography>
              {analysis && (
                <Typography variant="caption" color="text.secondary">
                  {language === 'ar' ? 'آخر تحليل: ' : 'Last analyzed: '}
                  {format(parseISO(analysis.analysis_date), 'PPP', { locale })}
                </Typography>
              )}
            </Box>
          </Box>
          
          <Stack direction="row" spacing={2}>
            {onCompare && (
              <Button
                variant="outlined"
                startIcon={<CompareArrows />}
                onClick={() => onCompare(competitor.id)}
              >
                {language === 'ar' ? 'مقارنة' : 'Compare'}
              </Button>
            )}
            {onRefresh && (
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={onRefresh}
                disabled={loading}
              >
                {language === 'ar' ? 'تحديث التحليل' : 'Update Analysis'}
              </Button>
            )}
          </Stack>
        </Box>
      </Paper>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label={language === 'ar' ? 'نظرة عامة' : 'Overview'} />
          <Tab label={language === 'ar' ? 'التفاعل' : 'Engagement'} />
          <Tab label={language === 'ar' ? 'أنماط النشر' : 'Posting Patterns'} />
          <Tab label={language === 'ar' ? 'الهاشتاقات' : 'Hashtags'} />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <TabPanel value={activeTab} index={0}>
        {renderOverview()}
      </TabPanel>
      <TabPanel value={activeTab} index={1}>
        {renderEngagement()}
      </TabPanel>
      <TabPanel value={activeTab} index={2}>
        {renderPostingPatterns()}
      </TabPanel>
      <TabPanel value={activeTab} index={3}>
        {renderHashtags()}
      </TabPanel>
    </Box>
  );
};