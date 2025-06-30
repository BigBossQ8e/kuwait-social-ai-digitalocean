// Competitor comparison component with side-by-side analysis

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  Avatar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Stack,
  Divider,
  Button,
  Alert,
  useTheme,
  alpha,
  IconButton,
  Tooltip,
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
  Speed,
  EmojiEvents,
  CompareArrows,
  SwapHoriz,
  Info,
  CheckCircle,
  Cancel,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import type { Competitor, CompetitorAnalysis } from '../../../types/api.types';

interface CompetitorComparisonProps {
  competitors: Competitor[];
  yourBusiness?: {
    name: string;
    metrics: CompetitorAnalysis;
  };
  onSelectCompetitors?: (competitorIds: number[]) => void;
}

interface ComparisonMetric {
  metric: string;
  metricAr: string;
  you: number;
  competitor1: number;
  competitor2?: number;
  unit?: string;
  higherIsBetter?: boolean;
}

const platformColors: Record<string, string> = {
  instagram: '#E4405F',
  twitter: '#1DA1F2',
  snapchat: '#FFFC00',
};

// Mock data for demonstration
const generateComparisonData = (): ComparisonMetric[] => [
  {
    metric: 'Followers',
    metricAr: 'المتابعون',
    you: 5420,
    competitor1: 8200,
    competitor2: 6500,
    higherIsBetter: true,
  },
  {
    metric: 'Engagement Rate',
    metricAr: 'معدل التفاعل',
    you: 4.2,
    competitor1: 3.8,
    competitor2: 5.1,
    unit: '%',
    higherIsBetter: true,
  },
  {
    metric: 'Posts/Week',
    metricAr: 'منشورات/أسبوع',
    you: 5,
    competitor1: 7,
    competitor2: 4,
    higherIsBetter: true,
  },
  {
    metric: 'Avg. Likes',
    metricAr: 'متوسط الإعجابات',
    you: 234,
    competitor1: 312,
    competitor2: 189,
    higherIsBetter: true,
  },
  {
    metric: 'Avg. Comments',
    metricAr: 'متوسط التعليقات',
    you: 45,
    competitor1: 67,
    competitor2: 32,
    higherIsBetter: true,
  },
  {
    metric: 'Response Time (hrs)',
    metricAr: 'وقت الاستجابة (ساعة)',
    you: 2.5,
    competitor1: 4.2,
    competitor2: 1.8,
    higherIsBetter: false,
  },
];

const generateRadarData = () => [
  { metric: 'Content Quality', you: 85, competitor1: 75, competitor2: 90 },
  { metric: 'Consistency', you: 70, competitor1: 90, competitor2: 60 },
  { metric: 'Engagement', you: 65, competitor1: 60, competitor2: 85 },
  { metric: 'Growth', you: 80, competitor1: 70, competitor2: 75 },
  { metric: 'Innovation', you: 75, competitor1: 65, competitor2: 80 },
  { metric: 'Audience Loyalty', you: 90, competitor1: 85, competitor2: 70 },
];

const generateGrowthData = () => {
  const data = [];
  for (let i = 6; i >= 0; i--) {
    data.push({
      month: `Month ${7 - i}`,
      you: 5000 + i * 100 + Math.random() * 200,
      competitor1: 7000 + i * 150 + Math.random() * 300,
      competitor2: 6000 + i * 80 + Math.random() * 250,
    });
  }
  return data;
};

export const CompetitorComparison: React.FC<CompetitorComparisonProps> = ({
  competitors,
  yourBusiness,
  onSelectCompetitors,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  
  const [selectedCompetitor1, setSelectedCompetitor1] = useState<number | ''>(
    competitors[0]?.id || ''
  );
  const [selectedCompetitor2, setSelectedCompetitor2] = useState<number | ''>(
    competitors[1]?.id || ''
  );

  const comparisonData = generateComparisonData();
  const radarData = generateRadarData();
  const growthData = generateGrowthData();

  const competitor1 = competitors.find(c => c.id === selectedCompetitor1);
  const competitor2 = competitors.find(c => c.id === selectedCompetitor2);

  const handleSwapCompetitors = () => {
    const temp = selectedCompetitor1;
    setSelectedCompetitor1(selectedCompetitor2);
    setSelectedCompetitor2(temp);
  };

  const getWinner = (metric: ComparisonMetric) => {
    const values = [metric.you, metric.competitor1];
    if (metric.competitor2 !== undefined) values.push(metric.competitor2);
    
    const best = metric.higherIsBetter !== false 
      ? Math.max(...values)
      : Math.min(...values);
    
    if (metric.you === best) return 'you';
    if (metric.competitor1 === best) return 'competitor1';
    if (metric.competitor2 === best) return 'competitor2';
    return null;
  };

  const calculateOverallScore = (competitorData: any) => {
    // Mock calculation
    return Math.floor(Math.random() * 20) + 70;
  };

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h5" gutterBottom>
          {language === 'ar' ? 'مقارنة المنافسين' : 'Competitor Comparison'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {language === 'ar' 
            ? 'قارن أداء عملك مع المنافسين لتحديد الفرص والتحسينات'
            : 'Compare your business performance with competitors to identify opportunities and improvements'
          }
        </Typography>
      </Box>

      {/* Competitor Selection */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid xs={12} md={5}>
            <FormControl fullWidth>
              <InputLabel>{language === 'ar' ? 'المنافس الأول' : 'Competitor 1'}</InputLabel>
              <Select
                value={selectedCompetitor1}
                onChange={(e) => setSelectedCompetitor1(e.target.value as number)}
                label={language === 'ar' ? 'المنافس الأول' : 'Competitor 1'}
              >
                {competitors.map(comp => (
                  <MenuItem 
                    key={comp.id} 
                    value={comp.id}
                    disabled={comp.id === selectedCompetitor2}
                  >
                    <Box display="flex" alignItems="center" gap={1}>
                      {platformColors[comp.platform] === platformColors.instagram && <Instagram fontSize="small" />}
                      {platformColors[comp.platform] === platformColors.twitter && <Twitter fontSize="small" />}
                      {platformColors[comp.platform] === platformColors.snapchat && <CameraAlt fontSize="small" />}
                      {comp.name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid xs={12} md={2} display="flex" justifyContent="center">
            <IconButton onClick={handleSwapCompetitors} size="large">
              <SwapHoriz />
            </IconButton>
          </Grid>
          
          <Grid xs={12} md={5}>
            <FormControl fullWidth>
              <InputLabel>{language === 'ar' ? 'المنافس الثاني' : 'Competitor 2'}</InputLabel>
              <Select
                value={selectedCompetitor2}
                onChange={(e) => setSelectedCompetitor2(e.target.value as number)}
                label={language === 'ar' ? 'المنافس الثاني' : 'Competitor 2'}
              >
                <MenuItem value="">
                  <em>{language === 'ar' ? 'بدون' : 'None'}</em>
                </MenuItem>
                {competitors.map(comp => (
                  <MenuItem 
                    key={comp.id} 
                    value={comp.id}
                    disabled={comp.id === selectedCompetitor1}
                  >
                    <Box display="flex" alignItems="center" gap={1}>
                      {platformColors[comp.platform] === platformColors.instagram && <Instagram fontSize="small" />}
                      {platformColors[comp.platform] === platformColors.twitter && <Twitter fontSize="small" />}
                      {platformColors[comp.platform] === platformColors.snapchat && <CameraAlt fontSize="small" />}
                      {comp.name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Overall Score Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid xs={12} md={selectedCompetitor2 ? 4 : 6}>
          <Card sx={{ 
            background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
            color: 'white'
          }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h6" sx={{ opacity: 0.9 }}>
                    {yourBusiness?.name || (language === 'ar' ? 'عملك' : 'Your Business')}
                  </Typography>
                  <Typography variant="h3" sx={{ mt: 1 }}>
                    {calculateOverallScore(yourBusiness)}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    {language === 'ar' ? 'النقاط الإجمالية' : 'Overall Score'}
                  </Typography>
                </Box>
                <EmojiEvents sx={{ fontSize: 64, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {competitor1 && (
          <Grid xs={12} md={selectedCompetitor2 ? 4 : 6}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="h6" color="text.secondary">
                      {competitor1.name}
                    </Typography>
                    <Typography variant="h3" sx={{ mt: 1 }}>
                      {calculateOverallScore(competitor1)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {language === 'ar' ? 'النقاط الإجمالية' : 'Overall Score'}
                    </Typography>
                  </Box>
                  <Avatar sx={{ 
                    width: 64, 
                    height: 64, 
                    bgcolor: alpha(platformColors[competitor1.platform], 0.1) 
                  }}>
                    {platformColors[competitor1.platform] === platformColors.instagram && <Instagram />}
                    {platformColors[competitor1.platform] === platformColors.twitter && <Twitter />}
                    {platformColors[competitor1.platform] === platformColors.snapchat && <CameraAlt />}
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
        
        {competitor2 && selectedCompetitor2 && (
          <Grid xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="h6" color="text.secondary">
                      {competitor2.name}
                    </Typography>
                    <Typography variant="h3" sx={{ mt: 1 }}>
                      {calculateOverallScore(competitor2)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {language === 'ar' ? 'النقاط الإجمالية' : 'Overall Score'}
                    </Typography>
                  </Box>
                  <Avatar sx={{ 
                    width: 64, 
                    height: 64, 
                    bgcolor: alpha(platformColors[competitor2.platform], 0.1) 
                  }}>
                    {platformColors[competitor2.platform] === platformColors.instagram && <Instagram />}
                    {platformColors[competitor2.platform] === platformColors.twitter && <Twitter />}
                    {platformColors[competitor2.platform] === platformColors.snapchat && <CameraAlt />}
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Metrics Comparison Table */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          {language === 'ar' ? 'مقارنة المقاييس' : 'Metrics Comparison'}
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{language === 'ar' ? 'المقياس' : 'Metric'}</TableCell>
                <TableCell align="center">
                  {yourBusiness?.name || (language === 'ar' ? 'أنت' : 'You')}
                </TableCell>
                {competitor1 && (
                  <TableCell align="center">{competitor1.name}</TableCell>
                )}
                {competitor2 && selectedCompetitor2 && (
                  <TableCell align="center">{competitor2.name}</TableCell>
                )}
                <TableCell align="center">
                  {language === 'ar' ? 'الفائز' : 'Winner'}
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {comparisonData.map((row, index) => {
                const winner = getWinner(row);
                return (
                  <TableRow key={index}>
                    <TableCell>
                      <Typography variant="body2">
                        {language === 'ar' ? row.metricAr : row.metric}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={`${row.you}${row.unit || ''}`}
                        color={winner === 'you' ? 'success' : 'default'}
                        variant={winner === 'you' ? 'filled' : 'outlined'}
                      />
                    </TableCell>
                    {competitor1 && (
                      <TableCell align="center">
                        <Chip
                          label={`${row.competitor1}${row.unit || ''}`}
                          color={winner === 'competitor1' ? 'success' : 'default'}
                          variant={winner === 'competitor1' ? 'filled' : 'outlined'}
                        />
                      </TableCell>
                    )}
                    {competitor2 && selectedCompetitor2 && (
                      <TableCell align="center">
                        <Chip
                          label={`${row.competitor2}${row.unit || ''}`}
                          color={winner === 'competitor2' ? 'success' : 'default'}
                          variant={winner === 'competitor2' ? 'filled' : 'outlined'}
                        />
                      </TableCell>
                    )}
                    <TableCell align="center">
                      {winner === 'you' && <CheckCircle color="success" />}
                      {winner === 'competitor1' && competitor1 && (
                        <Chip
                          size="small"
                          label={competitor1.name}
                          sx={{ 
                            bgcolor: alpha(platformColors[competitor1.platform], 0.1),
                            color: platformColors[competitor1.platform]
                          }}
                        />
                      )}
                      {winner === 'competitor2' && competitor2 && (
                        <Chip
                          size="small"
                          label={competitor2.name}
                          sx={{ 
                            bgcolor: alpha(platformColors[competitor2.platform], 0.1),
                            color: platformColors[competitor2.platform]
                          }}
                        />
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Performance Radar */}
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'رادار الأداء' : 'Performance Radar'}
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name={yourBusiness?.name || 'You'}
                  dataKey="you"
                  stroke={theme.palette.primary.main}
                  fill={theme.palette.primary.main}
                  fillOpacity={0.3}
                />
                {competitor1 && (
                  <Radar
                    name={competitor1.name}
                    dataKey="competitor1"
                    stroke={platformColors[competitor1.platform]}
                    fill={platformColors[competitor1.platform]}
                    fillOpacity={0.3}
                  />
                )}
                {competitor2 && selectedCompetitor2 && (
                  <Radar
                    name={competitor2.name}
                    dataKey="competitor2"
                    stroke={platformColors[competitor2.platform]}
                    fill={platformColors[competitor2.platform]}
                    fillOpacity={0.3}
                  />
                )}
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Growth Trend */}
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'اتجاه النمو' : 'Growth Trend'}
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={growthData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="you"
                  name={yourBusiness?.name || 'You'}
                  stroke={theme.palette.primary.main}
                  strokeWidth={2}
                />
                {competitor1 && (
                  <Line
                    type="monotone"
                    dataKey="competitor1"
                    name={competitor1.name}
                    stroke={platformColors[competitor1.platform]}
                    strokeWidth={2}
                  />
                )}
                {competitor2 && selectedCompetitor2 && (
                  <Line
                    type="monotone"
                    dataKey="competitor2"
                    name={competitor2.name}
                    stroke={platformColors[competitor2.platform]}
                    strokeWidth={2}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Key Insights */}
        <Grid xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'الرؤى الرئيسية' : 'Key Insights'}
            </Typography>
            <Grid container spacing={2}>
              <Grid xs={12} md={4}>
                <Alert severity="success" icon={<TrendingUp />}>
                  <Typography variant="subtitle2" gutterBottom>
                    {language === 'ar' ? 'نقاط القوة' : 'Strengths'}
                  </Typography>
                  <Typography variant="body2">
                    {language === 'ar' 
                      ? 'معدل تفاعل أعلى من المنافس الأول'
                      : 'Higher engagement rate than competitor 1'
                    }
                  </Typography>
                </Alert>
              </Grid>
              <Grid xs={12} md={4}>
                <Alert severity="warning" icon={<Info />}>
                  <Typography variant="subtitle2" gutterBottom>
                    {language === 'ar' ? 'فرص التحسين' : 'Opportunities'}
                  </Typography>
                  <Typography variant="body2">
                    {language === 'ar' 
                      ? 'زيادة تكرار النشر لمطابقة المنافسين'
                      : 'Increase posting frequency to match competitors'
                    }
                  </Typography>
                </Alert>
              </Grid>
              <Grid xs={12} md={4}>
                <Alert severity="info" icon={<Speed />}>
                  <Typography variant="subtitle2" gutterBottom>
                    {language === 'ar' ? 'توصيات' : 'Recommendations'}
                  </Typography>
                  <Typography variant="body2">
                    {language === 'ar' 
                      ? 'ركز على محتوى الفيديو للحصول على تفاعل أفضل'
                      : 'Focus on video content for better engagement'
                    }
                  </Typography>
                </Alert>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};