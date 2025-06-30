// Date range picker component for analytics

import React, { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  IconButton,
  Chip,
  useTheme,
  alpha,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  CalendarMonth,
  Close,
  ChevronLeft,
  ChevronRight,
  Today,
} from '@mui/icons-material';
import {
  format,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  subDays,
  subMonths,
  addDays,
  addMonths,
  isSameDay,
  isWithinInterval,
  isBefore,
  isAfter,
  startOfDay,
  endOfDay,
} from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';

interface DateRangePickerProps {
  startDate?: Date;
  endDate?: Date;
  onChange: (startDate: Date, endDate: Date) => void;
  maxDate?: Date;
  minDate?: Date;
  presets?: boolean;
}

type PresetRange = 'today' | 'yesterday' | 'last7days' | 'last30days' | 'thisMonth' | 'lastMonth' | 'custom';

interface PresetOption {
  value: PresetRange;
  label: string;
  labelAr: string;
  getRange: () => { start: Date; end: Date };
}

const presetOptions: PresetOption[] = [
  {
    value: 'today',
    label: 'Today',
    labelAr: 'اليوم',
    getRange: () => ({
      start: startOfDay(new Date()),
      end: endOfDay(new Date()),
    }),
  },
  {
    value: 'yesterday',
    label: 'Yesterday',
    labelAr: 'أمس',
    getRange: () => ({
      start: startOfDay(subDays(new Date(), 1)),
      end: endOfDay(subDays(new Date(), 1)),
    }),
  },
  {
    value: 'last7days',
    label: 'Last 7 days',
    labelAr: 'آخر 7 أيام',
    getRange: () => ({
      start: startOfDay(subDays(new Date(), 6)),
      end: endOfDay(new Date()),
    }),
  },
  {
    value: 'last30days',
    label: 'Last 30 days',
    labelAr: 'آخر 30 يوم',
    getRange: () => ({
      start: startOfDay(subDays(new Date(), 29)),
      end: endOfDay(new Date()),
    }),
  },
  {
    value: 'thisMonth',
    label: 'This month',
    labelAr: 'هذا الشهر',
    getRange: () => ({
      start: startOfMonth(new Date()),
      end: endOfDay(new Date()),
    }),
  },
  {
    value: 'lastMonth',
    label: 'Last month',
    labelAr: 'الشهر الماضي',
    getRange: () => {
      const lastMonth = subMonths(new Date(), 1);
      return {
        start: startOfMonth(lastMonth),
        end: endOfMonth(lastMonth),
      };
    },
  },
];

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  startDate: initialStartDate,
  endDate: initialEndDate,
  onChange,
  maxDate = new Date(),
  minDate,
  presets = true,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const locale = language === 'ar' ? ar : enUS;

  const [open, setOpen] = useState(false);
  const [startDate, setStartDate] = useState<Date | null>(initialStartDate || null);
  const [endDate, setEndDate] = useState<Date | null>(initialEndDate || null);
  const [selectedPreset, setSelectedPreset] = useState<PresetRange>('custom');
  const [viewMonth, setViewMonth] = useState(new Date());
  const [hoverDate, setHoverDate] = useState<Date | null>(null);

  const handlePresetChange = (
    event: React.MouseEvent<HTMLElement>,
    newPreset: PresetRange | null
  ) => {
    if (!newPreset) return;
    
    setSelectedPreset(newPreset);
    
    if (newPreset !== 'custom') {
      const preset = presetOptions.find(p => p.value === newPreset);
      if (preset) {
        const range = preset.getRange();
        setStartDate(range.start);
        setEndDate(range.end);
      }
    }
  };

  const handleDateClick = (date: Date) => {
    if (!startDate || (startDate && endDate)) {
      // Start new selection
      setStartDate(date);
      setEndDate(null);
      setSelectedPreset('custom');
    } else {
      // Complete selection
      if (isBefore(date, startDate)) {
        setEndDate(startDate);
        setStartDate(date);
      } else {
        setEndDate(date);
      }
    }
  };

  const handleApply = () => {
    if (startDate && endDate) {
      onChange(startDate, endDate);
      setOpen(false);
    }
  };

  const handleCancel = () => {
    setStartDate(initialStartDate || null);
    setEndDate(initialEndDate || null);
    setOpen(false);
  };

  const isDateInRange = (date: Date) => {
    if (!startDate || !endDate) return false;
    return isWithinInterval(date, { start: startDate, end: endDate });
  };

  const isDateHovered = (date: Date) => {
    if (!startDate || endDate || !hoverDate) return false;
    
    if (isBefore(hoverDate, startDate)) {
      return isWithinInterval(date, { start: hoverDate, end: startDate });
    } else {
      return isWithinInterval(date, { start: startDate, end: hoverDate });
    }
  };

  const isDateDisabled = (date: Date) => {
    if (minDate && isBefore(date, minDate)) return true;
    if (maxDate && isAfter(date, maxDate)) return true;
    return false;
  };

  const renderCalendarDay = (date: Date) => {
    const isSelected = (startDate && isSameDay(date, startDate)) || (endDate && isSameDay(date, endDate));
    const isInRange = isDateInRange(date);
    const isHovered = isDateHovered(date);
    const isDisabled = isDateDisabled(date);
    const isToday = isSameDay(date, new Date());

    return (
      <Box
        key={date.toISOString()}
        onClick={() => !isDisabled && handleDateClick(date)}
        onMouseEnter={() => setHoverDate(date)}
        onMouseLeave={() => setHoverDate(null)}
        sx={{
          aspectRatio: '1',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: isDisabled ? 'not-allowed' : 'pointer',
          borderRadius: 1,
          position: 'relative',
          opacity: isDisabled ? 0.3 : 1,
          backgroundColor: isSelected
            ? theme.palette.primary.main
            : isInRange || isHovered
            ? alpha(theme.palette.primary.main, 0.1)
            : 'transparent',
          color: isSelected ? theme.palette.primary.contrastText : 'inherit',
          border: isToday ? `2px solid ${theme.palette.primary.main}` : 'none',
          '&:hover': {
            backgroundColor: isDisabled
              ? 'transparent'
              : isSelected
              ? theme.palette.primary.dark
              : alpha(theme.palette.primary.main, 0.2),
          },
        }}
      >
        <Typography variant="body2">
          {format(date, 'd')}
        </Typography>
      </Box>
    );
  };

  const renderCalendarMonth = () => {
    const monthStart = startOfMonth(viewMonth);
    const monthEnd = endOfMonth(viewMonth);
    const calendarStart = startOfWeek(monthStart, { locale });
    const calendarEnd = endOfWeek(monthEnd, { locale });
    
    const days = [];
    let currentDate = calendarStart;
    
    while (currentDate <= calendarEnd) {
      days.push(new Date(currentDate));
      currentDate = addDays(currentDate, 1);
    }
    
    return days;
  };

  const formatDateRange = () => {
    if (startDate && endDate) {
      return `${format(startDate, 'MMM dd, yyyy', { locale })} - ${format(endDate, 'MMM dd, yyyy', { locale })}`;
    }
    return language === 'ar' ? 'اختر نطاق التاريخ' : 'Select date range';
  };

  return (
    <Box>
      <Button
        variant="outlined"
        startIcon={<CalendarMonth />}
        onClick={() => setOpen(true)}
        sx={{ minWidth: 200 }}
      >
        {formatDateRange()}
      </Button>

      <Dialog
        open={open}
        onClose={handleCancel}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {language === 'ar' ? 'اختر نطاق التاريخ' : 'Select Date Range'}
            </Typography>
            <IconButton onClick={handleCancel} size="small">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          <Grid container spacing={3}>
            {/* Preset Options */}
            {presets && (
              <Grid xs={12}>
                <ToggleButtonGroup
                  value={selectedPreset}
                  exclusive
                  onChange={handlePresetChange}
                  size="small"
                  sx={{ flexWrap: 'wrap', gap: 1 }}
                >
                  {presetOptions.map(option => (
                    <ToggleButton key={option.value} value={option.value}>
                      {language === 'ar' ? option.labelAr : option.label}
                    </ToggleButton>
                  ))}
                </ToggleButtonGroup>
              </Grid>
            )}

            {/* Date Inputs */}
            <Grid xs={12} sm={6}>
              <TextField
                label={language === 'ar' ? 'تاريخ البداية' : 'Start Date'}
                type="date"
                value={startDate ? format(startDate, 'yyyy-MM-dd') : ''}
                onChange={(e) => {
                  const date = e.target.value ? new Date(e.target.value) : null;
                  setStartDate(date);
                  setSelectedPreset('custom');
                }}
                fullWidth
                InputLabelProps={{ shrink: true }}
                inputProps={{
                  max: maxDate ? format(maxDate, 'yyyy-MM-dd') : undefined,
                  min: minDate ? format(minDate, 'yyyy-MM-dd') : undefined,
                }}
              />
            </Grid>
            <Grid xs={12} sm={6}>
              <TextField
                label={language === 'ar' ? 'تاريخ النهاية' : 'End Date'}
                type="date"
                value={endDate ? format(endDate, 'yyyy-MM-dd') : ''}
                onChange={(e) => {
                  const date = e.target.value ? new Date(e.target.value) : null;
                  setEndDate(date);
                  setSelectedPreset('custom');
                }}
                fullWidth
                InputLabelProps={{ shrink: true }}
                inputProps={{
                  max: maxDate ? format(maxDate, 'yyyy-MM-dd') : undefined,
                  min: startDate ? format(startDate, 'yyyy-MM-dd') : 
                       minDate ? format(minDate, 'yyyy-MM-dd') : undefined,
                }}
              />
            </Grid>

            {/* Calendar */}
            <Grid xs={12}>
              <Box>
                {/* Calendar Header */}
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <IconButton onClick={() => setViewMonth(subMonths(viewMonth, 1))}>
                    {language === 'ar' ? <ChevronRight /> : <ChevronLeft />}
                  </IconButton>
                  
                  <Typography variant="h6">
                    {format(viewMonth, 'MMMM yyyy', { locale })}
                  </Typography>
                  
                  <IconButton onClick={() => setViewMonth(addMonths(viewMonth, 1))}>
                    {language === 'ar' ? <ChevronLeft /> : <ChevronRight />}
                  </IconButton>
                </Box>

                {/* Week Days */}
                <Box
                  display="grid"
                  gridTemplateColumns="repeat(7, 1fr)"
                  gap={1}
                  mb={1}
                >
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <Typography
                      key={day}
                      variant="caption"
                      align="center"
                      color="text.secondary"
                      fontWeight="bold"
                    >
                      {language === 'ar' 
                        ? ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'][
                            ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(day)
                          ]
                        : day
                      }
                    </Typography>
                  ))}
                </Box>

                {/* Calendar Days */}
                <Box
                  display="grid"
                  gridTemplateColumns="repeat(7, 1fr)"
                  gap={1}
                >
                  {renderCalendarMonth().map(renderCalendarDay)}
                </Box>
              </Box>
            </Grid>

            {/* Selected Range Display */}
            {startDate && endDate && (
              <Grid xs={12}>
                <Chip
                  icon={<CalendarMonth />}
                  label={formatDateRange()}
                  color="primary"
                  sx={{ mr: 1 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1}{' '}
                  {language === 'ar' ? 'أيام' : 'days'}
                </Typography>
              </Grid>
            )}
          </Grid>
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setViewMonth(new Date())} startIcon={<Today />}>
            {language === 'ar' ? 'اليوم' : 'Today'}
          </Button>
          <Box flex={1} />
          <Button onClick={handleCancel}>
            {language === 'ar' ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button
            variant="contained"
            onClick={handleApply}
            disabled={!startDate || !endDate}
          >
            {language === 'ar' ? 'تطبيق' : 'Apply'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};