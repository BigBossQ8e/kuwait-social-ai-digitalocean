// Performance metrics component with detailed insights

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Menu,
  MenuItem,
  Divider,
  Stack,
  useTheme,
  alpha,
  Tooltip,
  Alert,
  Rating,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  TrendingUp,
  TrendingDown,
  Instagram,
  Twitter,
  CameraAlt,
  Speed,
  Timer,
  ThumbUp,
  ChatBubble,
  Share,
  Visibility,
  AccessTime,
  CalendarMonth,
  Info,
  MoreVert,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  EmojiEvents,
  LocalFireDepartment,
  ArrowUpward,
  ArrowDownward,
} from '@mui/icons-material';
import { format, formatDistanceToNow, subDays } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';

interface PerformanceMetricsProps {
  clientId?: number;
  dateRange?: { start: Date; end: Date };
  loading?: boolean;
  onActionClick?: (action: string, data?: any) => void;
}

interface MetricScore {
  label: string;
  labelAr: string;
  value: number;
  max: number;
  status: 'excellent' | 'good' | 'average' | 'poor';
  tips: string[];
  tipsAr: string[];
}

interface ContentInsight {
  type: string;
  description: string;
  descriptionAr: string;
  impact: 'high' | 'medium' | 'low';
  actionable: boolean;
}

const platformIcons: Record<string, React.ReactNode> = {
  instagram: <Instagram />,
  twitter: <Twitter />,
  snapchat: <CameraAlt />,
};

const platformColors: Record<string, string> = {
  instagram: '#E4405F',
  twitter: '#1DA1F2',
  snapchat: '#FFFC00',
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'excellent':
      return 'success';
    case 'good':
      return 'info';
    case 'average':
      return 'warning';
    case 'poor':
      return 'error';
    default:
      return 'default';
  }
};

const MetricCard: React.FC<{
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  color?: string;
  subtitle?: string;
  onClick?: () => void;
}> = ({ title, value, change, icon, color, subtitle, onClick }) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);

  return (
    <Card 
      sx={{ 
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s',
        '&:hover': onClick ? {
          boxShadow: theme.shadows[4],
          transform: 'translateY(-2px)',
        } : {},
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Avatar
            sx={{
              backgroundColor: color ? alpha(color, 0.1) : alpha(theme.palette.primary.main, 0.1),
              color: color || theme.palette.primary.main,
              width: 48,
              height: 48,
            }}
          >
            {icon}
          </Avatar>
          {change !== undefined && (
            <Chip
              size="small"
              icon={change > 0 ? <ArrowUpward fontSize="small" /> : <ArrowDownward fontSize="small" />}
              label={`${Math.abs(change)}%`}
              color={change > 0 ? 'success' : 'error'}
              sx={{ borderRadius: 1 }}
            />
          )}
        </Box>
        
        <Typography variant="h4" component="div" gutterBottom>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </Typography>
        
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
        
        {subtitle && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

const ScoreCard: React.FC<{ score: MetricScore }> = ({ score }) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const progress = (score.value / score.max) * 100;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
        <Typography variant="subtitle2">
          {language === 'ar' ? score.labelAr : score.label}
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip
            label={score.status}
            size="small"
            color={getStatusColor(score.status) as any}
          />
          <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)}>
            <Info fontSize="small" />
          </IconButton>
        </Box>
      </Box>
      
      <Box position="relative" mb={2}>
        <LinearProgress
          variant="determinate"
          value={progress}
          sx={{
            height: 8,
            borderRadius: 4,
            backgroundColor: theme.palette.grey[200],
            '& .MuiLinearProgress-bar': {
              backgroundColor: theme.palette[getStatusColor(score.status) as keyof typeof theme.palette].main,
            },
          }}
        />
        <Typography
          variant="caption"
          sx={{
            position: 'absolute',
            right: 0,
            top: -20,
            fontWeight: 'bold',
          }}
        >
          {score.value}/{score.max}
        </Typography>
      </Box>
      
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
        PaperProps={{ sx: { maxWidth: 300 } }}
      >
        <Box p={2}>
          <Typography variant="subtitle2" gutterBottom>
            {language === 'ar' ? 'نصائح للتحسين' : 'Improvement Tips'}
          </Typography>
          <List dense>
            {(language === 'ar' ? score.tipsAr : score.tips).map((tip, index) => (
              <ListItem key={index} disablePadding>
                <ListItemText primary={`• ${tip}`} />
              </ListItem>
            ))}
          </List>
        </Box>
      </Menu>
    </Box>
  );
};

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  clientId,
  dateRange,
  loading = false,
  onActionClick,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const locale = language === 'ar' ? ar : enUS;

  // Mock performance scores
  const performanceScores: MetricScore[] = [
    {
      label: 'Engagement Rate',
      labelAr: 'معدل التفاعل',
      value: 4.2,
      max: 10,
      status: 'average',
      tips: [
        'Post more consistently',
        'Use trending hashtags',
        'Engage with your audience',
      ],
      tipsAr: [
        'انشر بشكل أكثر انتظامًا',
        'استخدم الهاشتاقات الرائجة',
        'تفاعل مع جمهورك',
      ],
    },
    {
      label: 'Content Quality',
      labelAr: 'جودة المحتوى',
      value: 8,
      max: 10,
      status: 'good',
      tips: [
        'Continue using high-quality images',
        'Add more video content',
      ],
      tipsAr: [
        'استمر في استخدام صور عالية الجودة',
        'أضف المزيد من محتوى الفيديو',
      ],
    },
    {
      label: 'Posting Consistency',
      labelAr: 'انتظام النشر',
      value: 6,
      max: 10,
      status: 'average',
      tips: [
        'Maintain a regular posting schedule',
        'Use content calendar',
      ],
      tipsAr: [
        'حافظ على جدول نشر منتظم',
        'استخدم تقويم المحتوى',
      ],
    },
    {
      label: 'Hashtag Performance',
      labelAr: 'أداء الهاشتاقات',
      value: 9,
      max: 10,
      status: 'excellent',
      tips: [
        'Keep using localized hashtags',
      ],
      tipsAr: [
        'استمر في استخدام الهاشتاقات المحلية',
      ],
    },
  ];

  // Mock content insights
  const contentInsights: ContentInsight[] = [
    {
      type: 'timing',
      description: 'Posts published at 7 PM get 45% more engagement',
      descriptionAr: 'المنشورات المنشورة في 7 مساءً تحصل على تفاعل أكثر بنسبة 45%',
      impact: 'high',
      actionable: true,
    },
    {
      type: 'content',
      description: 'Video content performs 3x better than images',
      descriptionAr: 'محتوى الفيديو يؤدي أفضل 3 مرات من الصور',
      impact: 'high',
      actionable: true,
    },
    {
      type: 'hashtags',
      description: '#Kuwait and #Q8 are your top performing hashtags',
      descriptionAr: '#الكويت و #Q8 هي أفضل الهاشتاقات أداءً',
      impact: 'medium',
      actionable: false,
    },
    {
      type: 'audience',
      description: 'Your audience is most active on weekends',
      descriptionAr: 'جمهورك أكثر نشاطًا في عطلات نهاية الأسبوع',
      impact: 'medium',
      actionable: true,
    },
  ];

  // Mock competitor comparison
  const competitorComparison = [
    { metric: 'Followers', you: 5420, competitor: 8200, unit: '' },
    { metric: 'Engagement Rate', you: 4.2, competitor: 3.8, unit: '%' },
    { metric: 'Posts/Week', you: 5, competitor: 7, unit: '' },
    { metric: 'Avg. Likes', you: 234, competitor: 312, unit: '' },
  ];

  const overallScore = performanceScores.reduce((acc, score) => acc + score.value, 0) / performanceScores.length;

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          {language === 'ar' ? 'مقاييس الأداء' : 'Performance Metrics'}
        </Typography>
        
        <Button
          variant="outlined"
          startIcon={<CalendarMonth />}
          onClick={() => onActionClick?.('changeDateRange')}
        >
          {dateRange
            ? `${format(dateRange.start, 'MMM dd')} - ${format(dateRange.end, 'MMM dd')}`
            : language === 'ar' ? 'آخر 30 يوم' : 'Last 30 days'
          }
        </Button>
      </Box>

      {/* Overall Performance Score */}
      <Paper sx={{ p: 3, mb: 3, background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)` }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" color="white" gutterBottom>
              {language === 'ar' ? 'النتيجة الإجمالية' : 'Overall Score'}
            </Typography>
            <Box display="flex" alignItems="baseline" gap={1}>
              <Typography variant="h2" color="white">
                {overallScore.toFixed(1)}
              </Typography>
              <Typography variant="h5" color="white" sx={{ opacity: 0.8 }}>
                /10
              </Typography>
            </Box>
            <Rating
              value={overallScore / 2}
              readOnly
              precision={0.5}
              sx={{
                '& .MuiRating-iconFilled': {
                  color: theme.palette.common.white,
                },
                '& .MuiRating-iconEmpty': {
                  color: alpha(theme.palette.common.white, 0.3),
                },
              }}
            />
          </Box>
          
          <EmojiEvents sx={{ fontSize: 80, color: alpha(theme.palette.common.white, 0.2) }} />
        </Box>
      </Paper>

      {/* Key Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid xs={12} sm={6} md={3}>
          <MetricCard
            title={language === 'ar' ? 'إجمالي التفاعل' : 'Total Engagement'}
            value="12.5K"
            change={15}
            icon={<ThumbUp />}
            color={theme.palette.success.main}
            subtitle={language === 'ar' ? 'هذا الشهر' : 'This month'}
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <MetricCard
            title={language === 'ar' ? 'متوسط الوصول' : 'Average Reach'}
            value="8.2K"
            change={-5}
            icon={<Visibility />}
            color={theme.palette.info.main}
            subtitle={language === 'ar' ? 'لكل منشور' : 'Per post'}
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <MetricCard
            title={language === 'ar' ? 'وقت الاستجابة' : 'Response Time'}
            value="2.5h"
            change={20}
            icon={<Timer />}
            color={theme.palette.warning.main}
            subtitle={language === 'ar' ? 'متوسط' : 'Average'}
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <MetricCard
            title={language === 'ar' ? 'معدل النمو' : 'Growth Rate'}
            value="+12%"
            icon={<TrendingUp />}
            color={theme.palette.primary.main}
            subtitle={language === 'ar' ? 'مقارنة بالشهر الماضي' : 'vs last month'}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Performance Scores */}
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'نقاط الأداء' : 'Performance Scores'}
            </Typography>
            
            <Stack spacing={3}>
              {performanceScores.map((score, index) => (
                <ScoreCard key={index} score={score} />
              ))}
            </Stack>
            
            <Divider sx={{ my: 3 }} />
            
            <Alert severity="info" icon={<LocalFireDepartment />}>
              <Typography variant="body2">
                {language === 'ar'
                  ? 'نصيحة: ركز على تحسين معدل التفاعل من خلال النشر في الأوقات المثلى'
                  : 'Pro tip: Focus on improving engagement rate by posting at optimal times'
                }
              </Typography>
            </Alert>
          </Paper>
        </Grid>

        {/* Content Insights */}
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'رؤى المحتوى' : 'Content Insights'}
            </Typography>
            
            <List>
              {contentInsights.map((insight, index) => (
                <React.Fragment key={index}>
                  <ListItem
                    alignItems="flex-start"
                    secondaryAction={
                      insight.actionable && (
                        <Button
                          size="small"
                          onClick={() => onActionClick?.('applyInsight', insight)}
                        >
                          {language === 'ar' ? 'تطبيق' : 'Apply'}
                        </Button>
                      )
                    }
                  >
                    <ListItemAvatar>
                      <Avatar
                        sx={{
                          bgcolor: alpha(
                            insight.impact === 'high'
                              ? theme.palette.error.main
                              : insight.impact === 'medium'
                              ? theme.palette.warning.main
                              : theme.palette.info.main,
                            0.1
                          ),
                          color:
                            insight.impact === 'high'
                              ? theme.palette.error.main
                              : insight.impact === 'medium'
                              ? theme.palette.warning.main
                              : theme.palette.info.main,
                        }}
                      >
                        {insight.type === 'timing' && <AccessTime />}
                        {insight.type === 'content' && <Speed />}
                        {insight.type === 'hashtags' && <LocalFireDepartment />}
                        {insight.type === 'audience' && <ThumbUp />}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={language === 'ar' ? insight.descriptionAr : insight.description}
                      secondary={
                        <Chip
                          label={
                            insight.impact === 'high'
                              ? (language === 'ar' ? 'تأثير عالي' : 'High impact')
                              : insight.impact === 'medium'
                              ? (language === 'ar' ? 'تأثير متوسط' : 'Medium impact')
                              : (language === 'ar' ? 'تأثير منخفض' : 'Low impact')
                          }
                          size="small"
                          color={
                            insight.impact === 'high'
                              ? 'error'
                              : insight.impact === 'medium'
                              ? 'warning'
                              : 'info'
                          }
                          sx={{ mt: 1 }}
                        />
                      }
                    />
                  </ListItem>
                  {index < contentInsights.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Competitor Comparison */}
        <Grid xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                {language === 'ar' ? 'مقارنة مع المنافسين' : 'Competitor Comparison'}
              </Typography>
              <Button
                size="small"
                onClick={() => onActionClick?.('viewCompetitors')}
              >
                {language === 'ar' ? 'عرض الكل' : 'View All'}
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              {competitorComparison.map((item, index) => (
                <Grid xs={12} sm={6} md={3} key={index}>
                  <Box textAlign="center">
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      {item.metric}
                    </Typography>
                    <Box display="flex" justifyContent="center" alignItems="baseline" gap={2}>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          {language === 'ar' ? 'أنت' : 'You'}
                        </Typography>
                        <Typography
                          variant="h6"
                          color={item.you > item.competitor ? 'success.main' : 'text.primary'}
                        >
                          {item.you}{item.unit}
                        </Typography>
                      </Box>
                      <Typography variant="h6" color="text.secondary">
                        vs
                      </Typography>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          {language === 'ar' ? 'المنافس' : 'Competitor'}
                        </Typography>
                        <Typography
                          variant="h6"
                          color={item.competitor > item.you ? 'error.main' : 'text.primary'}
                        >
                          {item.competitor}{item.unit}
                        </Typography>
                      </Box>
                    </Box>
                    
                    {/* Progress comparison */}
                    <Box sx={{ mt: 1, position: 'relative', height: 8 }}>
                      <LinearProgress
                        variant="determinate"
                        value={(item.you / (item.you + item.competitor)) * 100}
                        sx={{
                          height: '100%',
                          borderRadius: 4,
                          backgroundColor: theme.palette.grey[200],
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: item.you > item.competitor
                              ? theme.palette.success.main
                              : theme.palette.grey[400],
                          },
                        }}
                      />
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};