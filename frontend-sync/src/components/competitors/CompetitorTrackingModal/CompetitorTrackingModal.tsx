// Competitor tracking modal for real-time monitoring setup

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  Checkbox,
  FormGroup,
  Select,
  MenuItem,
  InputLabel,
  Chip,
  Stack,
  Alert,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Divider,
  IconButton,
  InputAdornment,
  Avatar,
  useTheme,
  alpha,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Close,
  Instagram,
  Twitter,
  CameraAlt,
  Search,
  NotificationsActive,
  Schedule,
  Tag,
  TrendingUp,
  Assessment,
  CheckCircle,
  Info,
  Add,
  Remove,
} from '@mui/icons-material';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';

interface CompetitorTrackingModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (trackingConfig: TrackingConfig) => void;
  competitor?: {
    id: number;
    name: string;
    username: string;
    platform: string;
  };
}

export interface TrackingConfig {
  competitorId: number;
  trackingFrequency: 'daily' | 'weekly' | 'monthly';
  metricsToTrack: string[];
  alerts: {
    enabled: boolean;
    conditions: AlertCondition[];
  };
  contentAnalysis: {
    enabled: boolean;
    trackHashtags: boolean;
    trackPostingTimes: boolean;
    trackContentThemes: boolean;
  };
  competitiveInsights: {
    enabled: boolean;
    compareWithYourMetrics: boolean;
    generateReports: boolean;
  };
}

interface AlertCondition {
  metric: string;
  condition: 'increases' | 'decreases' | 'reaches';
  value: number;
  percentage?: boolean;
}

const trackingMetrics = [
  { value: 'followers', label: 'Followers Count', labelAr: 'عدد المتابعين', icon: <TrendingUp /> },
  { value: 'engagement', label: 'Engagement Rate', labelAr: 'معدل التفاعل', icon: <Assessment /> },
  { value: 'posts', label: 'Posting Frequency', labelAr: 'تكرار النشر', icon: <Schedule /> },
  { value: 'hashtags', label: 'Hashtag Usage', labelAr: 'استخدام الهاشتاقات', icon: <Tag /> },
];

const alertMetrics = [
  { value: 'followers', label: 'Followers', labelAr: 'المتابعون' },
  { value: 'engagement', label: 'Engagement Rate', labelAr: 'معدل التفاعل' },
  { value: 'posts_per_day', label: 'Posts per Day', labelAr: 'منشورات/يوم' },
];

export const CompetitorTrackingModal: React.FC<CompetitorTrackingModalProps> = ({
  open,
  onClose,
  onSave,
  competitor,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  
  const [activeStep, setActiveStep] = useState(0);
  const [trackingFrequency, setTrackingFrequency] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['followers', 'engagement']);
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [alertConditions, setAlertConditions] = useState<AlertCondition[]>([
    { metric: 'followers', condition: 'increases', value: 10, percentage: true },
  ]);
  const [contentAnalysisEnabled, setContentAnalysisEnabled] = useState(true);
  const [contentOptions, setContentOptions] = useState({
    trackHashtags: true,
    trackPostingTimes: true,
    trackContentThemes: false,
  });
  const [insightsEnabled, setInsightsEnabled] = useState(true);
  const [insightOptions, setInsightOptions] = useState({
    compareWithYourMetrics: true,
    generateReports: true,
  });

  const steps = [
    {
      label: language === 'ar' ? 'تكرار التتبع' : 'Tracking Frequency',
      icon: <Schedule />,
    },
    {
      label: language === 'ar' ? 'المقاييس المراد تتبعها' : 'Metrics to Track',
      icon: <Assessment />,
    },
    {
      label: language === 'ar' ? 'التنبيهات' : 'Alerts',
      icon: <NotificationsActive />,
    },
    {
      label: language === 'ar' ? 'تحليل المحتوى' : 'Content Analysis',
      icon: <Tag />,
    },
    {
      label: language === 'ar' ? 'الرؤى التنافسية' : 'Competitive Insights',
      icon: <TrendingUp />,
    },
  ];

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleMetricToggle = (metric: string) => {
    setSelectedMetrics(prev =>
      prev.includes(metric)
        ? prev.filter(m => m !== metric)
        : [...prev, metric]
    );
  };

  const handleAddAlertCondition = () => {
    setAlertConditions([
      ...alertConditions,
      { metric: 'engagement', condition: 'decreases', value: 5, percentage: true },
    ]);
  };

  const handleRemoveAlertCondition = (index: number) => {
    setAlertConditions(alertConditions.filter((_, i) => i !== index));
  };

  const handleUpdateAlertCondition = (index: number, field: keyof AlertCondition, value: any) => {
    const updated = [...alertConditions];
    updated[index] = { ...updated[index], [field]: value };
    setAlertConditions(updated);
  };

  const handleSave = () => {
    if (!competitor) return;
    
    const config: TrackingConfig = {
      competitorId: competitor.id,
      trackingFrequency,
      metricsToTrack: selectedMetrics,
      alerts: {
        enabled: alertsEnabled,
        conditions: alertConditions,
      },
      contentAnalysis: {
        enabled: contentAnalysisEnabled,
        ...contentOptions,
      },
      competitiveInsights: {
        enabled: insightsEnabled,
        ...insightOptions,
      },
    };
    
    onSave(config);
    onClose();
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {language === 'ar' 
                ? 'اختر عدد مرات تحديث بيانات المنافس'
                : 'Choose how often to update competitor data'
              }
            </Typography>
            <RadioGroup
              value={trackingFrequency}
              onChange={(e) => setTrackingFrequency(e.target.value as any)}
            >
              <FormControlLabel
                value="daily"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1">
                      {language === 'ar' ? 'يوميًا' : 'Daily'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {language === 'ar' 
                        ? 'الأفضل لتتبع المنافسين النشطين'
                        : 'Best for tracking active competitors'
                      }
                    </Typography>
                  </Box>
                }
              />
              <FormControlLabel
                value="weekly"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1">
                      {language === 'ar' ? 'أسبوعيًا' : 'Weekly'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {language === 'ar' 
                        ? 'موازنة جيدة بين البيانات والتكلفة'
                        : 'Good balance of data and cost'
                      }
                    </Typography>
                  </Box>
                }
              />
              <FormControlLabel
                value="monthly"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1">
                      {language === 'ar' ? 'شهريًا' : 'Monthly'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {language === 'ar' 
                        ? 'للحصول على نظرة عامة طويلة المدى'
                        : 'For long-term overview'
                      }
                    </Typography>
                  </Box>
                }
              />
            </RadioGroup>
          </Box>
        );

      case 1:
        return (
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {language === 'ar' 
                ? 'حدد المقاييس التي تريد مراقبتها'
                : 'Select metrics you want to monitor'
              }
            </Typography>
            <FormGroup>
              {trackingMetrics.map(metric => (
                <FormControlLabel
                  key={metric.value}
                  control={
                    <Checkbox
                      checked={selectedMetrics.includes(metric.value)}
                      onChange={() => handleMetricToggle(metric.value)}
                    />
                  }
                  label={
                    <Box display="flex" alignItems="center" gap={1}>
                      {metric.icon}
                      <Typography variant="body1">
                        {language === 'ar' ? metric.labelAr : metric.label}
                      </Typography>
                    </Box>
                  }
                />
              ))}
            </FormGroup>
          </Box>
        );

      case 2:
        return (
          <Box>
            <FormControlLabel
              control={
                <Checkbox
                  checked={alertsEnabled}
                  onChange={(e) => setAlertsEnabled(e.target.checked)}
                />
              }
              label={
                <Typography variant="body1">
                  {language === 'ar' ? 'تفعيل التنبيهات' : 'Enable Alerts'}
                </Typography>
              }
            />
            
            {alertsEnabled && (
              <Box mt={2}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {language === 'ar' 
                    ? 'سيتم إرسال تنبيه عندما:'
                    : 'Send alert when:'
                  }
                </Typography>
                
                {alertConditions.map((condition, index) => (
                  <Paper key={index} variant="outlined" sx={{ p: 2, mb: 1 }}>
                    <Grid container spacing={2} alignItems="center">
                      <Grid xs={4}>
                        <FormControl size="small" fullWidth>
                          <Select
                            value={condition.metric}
                            onChange={(e) => handleUpdateAlertCondition(index, 'metric', e.target.value)}
                          >
                            {alertMetrics.map(metric => (
                              <MenuItem key={metric.value} value={metric.value}>
                                {language === 'ar' ? metric.labelAr : metric.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid xs={3}>
                        <FormControl size="small" fullWidth>
                          <Select
                            value={condition.condition}
                            onChange={(e) => handleUpdateAlertCondition(index, 'condition', e.target.value)}
                          >
                            <MenuItem value="increases">
                              {language === 'ar' ? 'يزيد' : 'Increases'}
                            </MenuItem>
                            <MenuItem value="decreases">
                              {language === 'ar' ? 'ينقص' : 'Decreases'}
                            </MenuItem>
                            <MenuItem value="reaches">
                              {language === 'ar' ? 'يصل إلى' : 'Reaches'}
                            </MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid xs={3}>
                        <TextField
                          size="small"
                          type="number"
                          value={condition.value}
                          onChange={(e) => handleUpdateAlertCondition(index, 'value', Number(e.target.value))}
                          InputProps={{
                            endAdornment: condition.percentage && <InputAdornment position="end">%</InputAdornment>,
                          }}
                        />
                      </Grid>
                      <Grid xs={2}>
                        <IconButton
                          size="small"
                          onClick={() => handleRemoveAlertCondition(index)}
                          disabled={alertConditions.length === 1}
                        >
                          <Remove />
                        </IconButton>
                      </Grid>
                    </Grid>
                  </Paper>
                ))}
                
                <Button
                  startIcon={<Add />}
                  onClick={handleAddAlertCondition}
                  size="small"
                  sx={{ mt: 1 }}
                >
                  {language === 'ar' ? 'إضافة شرط' : 'Add Condition'}
                </Button>
              </Box>
            )}
          </Box>
        );

      case 3:
        return (
          <Box>
            <FormControlLabel
              control={
                <Checkbox
                  checked={contentAnalysisEnabled}
                  onChange={(e) => setContentAnalysisEnabled(e.target.checked)}
                />
              }
              label={
                <Typography variant="body1">
                  {language === 'ar' ? 'تفعيل تحليل المحتوى' : 'Enable Content Analysis'}
                </Typography>
              }
            />
            
            {contentAnalysisEnabled && (
              <Box mt={2} ml={3}>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={contentOptions.trackHashtags}
                        onChange={(e) => setContentOptions({
                          ...contentOptions,
                          trackHashtags: e.target.checked
                        })}
                      />
                    }
                    label={language === 'ar' ? 'تتبع الهاشتاقات المستخدمة' : 'Track hashtag usage'}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={contentOptions.trackPostingTimes}
                        onChange={(e) => setContentOptions({
                          ...contentOptions,
                          trackPostingTimes: e.target.checked
                        })}
                      />
                    }
                    label={language === 'ar' ? 'تحليل أوقات النشر' : 'Analyze posting times'}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={contentOptions.trackContentThemes}
                        onChange={(e) => setContentOptions({
                          ...contentOptions,
                          trackContentThemes: e.target.checked
                        })}
                      />
                    }
                    label={language === 'ar' ? 'تحديد مواضيع المحتوى' : 'Identify content themes'}
                  />
                </FormGroup>
              </Box>
            )}
          </Box>
        );

      case 4:
        return (
          <Box>
            <FormControlLabel
              control={
                <Checkbox
                  checked={insightsEnabled}
                  onChange={(e) => setInsightsEnabled(e.target.checked)}
                />
              }
              label={
                <Typography variant="body1">
                  {language === 'ar' ? 'تفعيل الرؤى التنافسية' : 'Enable Competitive Insights'}
                </Typography>
              }
            />
            
            {insightsEnabled && (
              <Box mt={2} ml={3}>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={insightOptions.compareWithYourMetrics}
                        onChange={(e) => setInsightOptions({
                          ...insightOptions,
                          compareWithYourMetrics: e.target.checked
                        })}
                      />
                    }
                    label={language === 'ar' ? 'مقارنة مع مقاييس عملك' : 'Compare with your metrics'}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={insightOptions.generateReports}
                        onChange={(e) => setInsightOptions({
                          ...insightOptions,
                          generateReports: e.target.checked
                        })}
                      />
                    }
                    label={language === 'ar' ? 'إنشاء تقارير أسبوعية' : 'Generate weekly reports'}
                  />
                </FormGroup>
                
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    {language === 'ar' 
                      ? 'ستحصل على رؤى قابلة للتنفيذ لتحسين استراتيجيتك'
                      : 'You\'ll get actionable insights to improve your strategy'
                    }
                  </Typography>
                </Alert>
              </Box>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box display="flex" alignItems="center" gap={2}>
            {competitor && (
              <Chip
                icon={
                  competitor.platform === 'instagram' ? <Instagram /> :
                  competitor.platform === 'twitter' ? <Twitter /> :
                  <CameraAlt />
                }
                label={competitor.name}
                sx={{
                  bgcolor: alpha(
                    competitor.platform === 'instagram' ? '#E4405F' :
                    competitor.platform === 'twitter' ? '#1DA1F2' :
                    '#FFFC00',
                    0.1
                  ),
                }}
              />
            )}
            <Typography variant="h6">
              {language === 'ar' ? 'إعداد تتبع المنافس' : 'Setup Competitor Tracking'}
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={index}>
              <StepLabel
                StepIconComponent={() => (
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      bgcolor: activeStep >= index ? 'primary.main' : 'grey.300',
                    }}
                  >
                    {activeStep > index ? <CheckCircle /> : step.icon}
                  </Avatar>
                )}
              >
                {step.label}
              </StepLabel>
              <StepContent>
                <Box py={2}>
                  {renderStepContent(index)}
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    {index === steps.length - 1 
                      ? (language === 'ar' ? 'إنهاء' : 'Finish')
                      : (language === 'ar' ? 'التالي' : 'Next')
                    }
                  </Button>
                  <Button
                    disabled={index === 0}
                    onClick={handleBack}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    {language === 'ar' ? 'السابق' : 'Back'}
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
        
        {activeStep === steps.length && (
          <Paper square elevation={0} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'ملخص التكوين' : 'Configuration Summary'}
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <Schedule />
                </ListItemIcon>
                <ListItemText
                  primary={language === 'ar' ? 'التكرار:' : 'Frequency:'}
                  secondary={trackingFrequency}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Assessment />
                </ListItemIcon>
                <ListItemText
                  primary={language === 'ar' ? 'المقاييس:' : 'Metrics:'}
                  secondary={`${selectedMetrics.length} selected`}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <NotificationsActive />
                </ListItemIcon>
                <ListItemText
                  primary={language === 'ar' ? 'التنبيهات:' : 'Alerts:'}
                  secondary={alertsEnabled ? 'Enabled' : 'Disabled'}
                />
              </ListItem>
            </List>
          </Paper>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          {language === 'ar' ? 'إلغاء' : 'Cancel'}
        </Button>
        <Button
          variant="contained"
          onClick={handleSave}
          disabled={activeStep !== steps.length}
        >
          {language === 'ar' ? 'بدء التتبع' : 'Start Tracking'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};