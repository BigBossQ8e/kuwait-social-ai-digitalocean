// Data export component for analytics and reports

import React, { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  Checkbox,
  FormGroup,
  Typography,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
  IconButton,
  Paper,
} from '@mui/material';
import {
  Download,
  Description,
  TableChart,
  PictureAsPdf,
  Close,
  CheckCircle,
  Info,
  CalendarMonth,
  Analytics,
  PostAdd,
  People,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { DateRangePicker } from '../DateRangePicker';

interface DataExportProps {
  onExport: (options: ExportOptions) => Promise<void>;
  availableData?: string[];
}

export interface ExportOptions {
  format: 'csv' | 'xlsx' | 'pdf';
  dataTypes: string[];
  dateRange: {
    start: Date;
    end: Date;
  };
  includeCharts: boolean;
  includeSummary: boolean;
  groupBy?: 'day' | 'week' | 'month' | 'platform';
}

interface DataTypeOption {
  value: string;
  label: string;
  labelAr: string;
  icon: React.ReactNode;
  description: string;
  descriptionAr: string;
}

const dataTypeOptions: DataTypeOption[] = [
  {
    value: 'posts',
    label: 'Posts',
    labelAr: 'المنشورات',
    icon: <PostAdd />,
    description: 'All posts with captions, hashtags, and scheduling info',
    descriptionAr: 'جميع المنشورات مع التعليقات والهاشتاقات ومعلومات الجدولة',
  },
  {
    value: 'analytics',
    label: 'Analytics',
    labelAr: 'التحليلات',
    icon: <Analytics />,
    description: 'Engagement metrics, reach, impressions, and performance data',
    descriptionAr: 'مقاييس التفاعل والوصول والانطباعات وبيانات الأداء',
  },
  {
    value: 'competitors',
    label: 'Competitor Analysis',
    labelAr: 'تحليل المنافسين',
    icon: <People />,
    description: 'Competitor metrics and comparison data',
    descriptionAr: 'مقاييس المنافسين وبيانات المقارنة',
  },
  {
    value: 'campaigns',
    label: 'Campaigns',
    labelAr: 'الحملات',
    icon: <Description />,
    description: 'Campaign performance and ROI metrics',
    descriptionAr: 'أداء الحملات ومقاييس العائد على الاستثمار',
  },
];

const formatOptions = [
  {
    value: 'csv',
    label: 'CSV',
    icon: <TableChart />,
    description: 'Comma-separated values, compatible with Excel',
    descriptionAr: 'قيم مفصولة بفواصل، متوافقة مع Excel',
  },
  {
    value: 'xlsx',
    label: 'Excel',
    icon: <Description />,
    description: 'Microsoft Excel workbook with multiple sheets',
    descriptionAr: 'مصنف Microsoft Excel مع أوراق متعددة',
  },
  {
    value: 'pdf',
    label: 'PDF',
    icon: <PictureAsPdf />,
    description: 'Formatted report with charts and visualizations',
    descriptionAr: 'تقرير منسق مع الرسوم البيانية والتصورات',
  },
];

export const DataExport: React.FC<DataExportProps> = ({
  onExport,
  availableData = ['posts', 'analytics', 'competitors', 'campaigns'],
}) => {
  const language = useAppSelector(selectLanguage);
  const locale = language === 'ar' ? ar : enUS;
  
  const [open, setOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState<'csv' | 'xlsx' | 'pdf'>('csv');
  const [selectedDataTypes, setSelectedDataTypes] = useState<string[]>(['analytics']);
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().setDate(new Date().getDate() - 30)),
    end: new Date(),
  });
  const [includeCharts, setIncludeCharts] = useState(true);
  const [includeSummary, setIncludeSummary] = useState(true);
  const [groupBy, setGroupBy] = useState<'day' | 'week' | 'month' | 'platform'>('day');
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  const handleDataTypeToggle = (dataType: string) => {
    setSelectedDataTypes(prev =>
      prev.includes(dataType)
        ? prev.filter(type => type !== dataType)
        : [...prev, dataType]
    );
  };

  const handleExport = async () => {
    if (selectedDataTypes.length === 0) return;
    
    setExporting(true);
    setExportSuccess(false);
    
    try {
      await onExport({
        format: exportFormat,
        dataTypes: selectedDataTypes,
        dateRange,
        includeCharts: exportFormat === 'pdf' ? includeCharts : false,
        includeSummary,
        groupBy,
      });
      
      setExportSuccess(true);
      setTimeout(() => {
        setOpen(false);
        setExportSuccess(false);
      }, 2000);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExporting(false);
    }
  };

  const getEstimatedSize = () => {
    const baseSize = selectedDataTypes.length * 500; // KB per data type
    const chartSize = includeCharts && exportFormat === 'pdf' ? 2000 : 0; // KB for charts
    const total = baseSize + chartSize;
    
    if (total < 1000) {
      return `~${total} KB`;
    } else {
      return `~${(total / 1000).toFixed(1)} MB`;
    }
  };

  return (
    <>
      <Button
        variant="contained"
        startIcon={<Download />}
        onClick={() => setOpen(true)}
      >
        {language === 'ar' ? 'تصدير البيانات' : 'Export Data'}
      </Button>

      <Dialog
        open={open}
        onClose={() => !exporting && setOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {language === 'ar' ? 'تصدير البيانات' : 'Export Data'}
            </Typography>
            <IconButton 
              onClick={() => setOpen(false)} 
              size="small"
              disabled={exporting}
            >
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          {exportSuccess ? (
            <Box
              display="flex"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              py={8}
            >
              <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {language === 'ar' ? 'تم التصدير بنجاح!' : 'Export Successful!'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {language === 'ar' 
                  ? 'سيتم تنزيل الملف تلقائيًا'
                  : 'Your file will be downloaded automatically'
                }
              </Typography>
            </Box>
          ) : (
            <>
              {/* Format Selection */}
              <Box mb={3}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  {language === 'ar' ? 'تنسيق التصدير' : 'Export Format'}
                </Typography>
                <RadioGroup
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value as any)}
                >
                  {formatOptions.map(option => (
                    <FormControlLabel
                      key={option.value}
                      value={option.value}
                      control={<Radio />}
                      label={
                        <Box display="flex" alignItems="center" gap={2}>
                          <Box display="flex" alignItems="center" gap={1}>
                            {option.icon}
                            <Typography variant="body1">{option.label}</Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {language === 'ar' ? option.descriptionAr : option.description}
                          </Typography>
                        </Box>
                      }
                    />
                  ))}
                </RadioGroup>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Data Type Selection */}
              <Box mb={3}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  {language === 'ar' ? 'البيانات المطلوب تصديرها' : 'Data to Export'}
                </Typography>
                <FormGroup>
                  {dataTypeOptions
                    .filter(option => availableData.includes(option.value))
                    .map(option => (
                      <FormControlLabel
                        key={option.value}
                        control={
                          <Checkbox
                            checked={selectedDataTypes.includes(option.value)}
                            onChange={() => handleDataTypeToggle(option.value)}
                          />
                        }
                        label={
                          <Box>
                            <Box display="flex" alignItems="center" gap={1}>
                              {option.icon}
                              <Typography variant="body1">
                                {language === 'ar' ? option.labelAr : option.label}
                              </Typography>
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                              {language === 'ar' ? option.descriptionAr : option.description}
                            </Typography>
                          </Box>
                        }
                      />
                    ))}
                </FormGroup>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Date Range */}
              <Box mb={3}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  {language === 'ar' ? 'نطاق التاريخ' : 'Date Range'}
                </Typography>
                <DateRangePicker
                  startDate={dateRange.start}
                  endDate={dateRange.end}
                  onChange={(start, end) => setDateRange({ start, end })}
                />
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Additional Options */}
              <Box mb={3}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  {language === 'ar' ? 'خيارات إضافية' : 'Additional Options'}
                </Typography>
                
                {exportFormat === 'pdf' && (
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={includeCharts}
                        onChange={(e) => setIncludeCharts(e.target.checked)}
                      />
                    }
                    label={language === 'ar' ? 'تضمين الرسوم البيانية' : 'Include Charts'}
                  />
                )}
                
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={includeSummary}
                      onChange={(e) => setIncludeSummary(e.target.checked)}
                    />
                  }
                  label={language === 'ar' ? 'تضمين ملخص تنفيذي' : 'Include Executive Summary'}
                />
                
                {selectedDataTypes.includes('analytics') && (
                  <Box mt={2}>
                    <FormControl size="small" fullWidth>
                      <Typography variant="body2" gutterBottom>
                        {language === 'ar' ? 'تجميع البيانات حسب' : 'Group Data By'}
                      </Typography>
                      <RadioGroup
                        row
                        value={groupBy}
                        onChange={(e) => setGroupBy(e.target.value as any)}
                      >
                        <FormControlLabel value="day" control={<Radio />} label={language === 'ar' ? 'يوم' : 'Day'} />
                        <FormControlLabel value="week" control={<Radio />} label={language === 'ar' ? 'أسبوع' : 'Week'} />
                        <FormControlLabel value="month" control={<Radio />} label={language === 'ar' ? 'شهر' : 'Month'} />
                        <FormControlLabel value="platform" control={<Radio />} label={language === 'ar' ? 'منصة' : 'Platform'} />
                      </RadioGroup>
                    </FormControl>
                  </Box>
                )}
              </Box>

              {/* Export Summary */}
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <Info fontSize="small" color="info" />
                  <Typography variant="subtitle2">
                    {language === 'ar' ? 'ملخص التصدير' : 'Export Summary'}
                  </Typography>
                </Box>
                
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary={language === 'ar' ? 'التنسيق:' : 'Format:'}
                      secondary={exportFormat.toUpperCase()}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary={language === 'ar' ? 'أنواع البيانات:' : 'Data Types:'}
                      secondary={selectedDataTypes.length + ' ' + (language === 'ar' ? 'محدد' : 'selected')}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary={language === 'ar' ? 'الفترة:' : 'Period:'}
                      secondary={`${format(dateRange.start, 'MMM dd', { locale })} - ${format(dateRange.end, 'MMM dd', { locale })}`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary={language === 'ar' ? 'الحجم المقدر:' : 'Estimated Size:'}
                      secondary={getEstimatedSize()}
                    />
                  </ListItem>
                </List>
              </Paper>

              <Alert severity="info" sx={{ mt: 2 }}>
                {language === 'ar' 
                  ? 'قد يستغرق التصدير بضع دقائق حسب حجم البيانات'
                  : 'Export may take a few minutes depending on data size'
                }
              </Alert>
            </>
          )}
        </DialogContent>

        {!exportSuccess && (
          <DialogActions>
            <Button onClick={() => setOpen(false)} disabled={exporting}>
              {language === 'ar' ? 'إلغاء' : 'Cancel'}
            </Button>
            <Button
              variant="contained"
              onClick={handleExport}
              disabled={selectedDataTypes.length === 0 || exporting}
              startIcon={exporting ? <CircularProgress size={20} /> : <Download />}
            >
              {exporting 
                ? (language === 'ar' ? 'جاري التصدير...' : 'Exporting...')
                : (language === 'ar' ? 'تصدير' : 'Export')
              }
            </Button>
          </DialogActions>
        )}
      </Dialog>
    </>
  );
};