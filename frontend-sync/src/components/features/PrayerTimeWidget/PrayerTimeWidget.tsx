// Prayer times widget for Kuwait-specific scheduling

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  Alert,
} from '@mui/material';
import {
  AccessTime,
  LocationOn,
  Schedule,
  CalendarToday,
  Refresh,
  Info,
} from '@mui/icons-material';
import { format, isToday, isTomorrow } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { LoadingSpinner } from '../../common/LoadingSpinner';

interface PrayerTime {
  name: string;
  nameAr: string;
  time: string;
  timestamp: Date;
  isPassed: boolean;
}

interface PrayerTimesData {
  date: string;
  location: string;
  times: PrayerTime[];
  nextPrayer?: PrayerTime;
}

// Mock prayer times data - will be replaced with API call
const mockPrayerTimes: PrayerTimesData = {
  date: new Date().toISOString().split('T')[0],
  location: 'Kuwait City',
  times: [
    {
      name: 'Fajr',
      nameAr: 'الفجر',
      time: '04:45',
      timestamp: new Date(new Date().setHours(4, 45, 0, 0)),
      isPassed: new Date().getHours() > 4 || (new Date().getHours() === 4 && new Date().getMinutes() > 45),
    },
    {
      name: 'Dhuhr',
      nameAr: 'الظهر',
      time: '11:52',
      timestamp: new Date(new Date().setHours(11, 52, 0, 0)),
      isPassed: new Date().getHours() > 11 || (new Date().getHours() === 11 && new Date().getMinutes() > 52),
    },
    {
      name: 'Asr',
      nameAr: 'العصر',
      time: '15:15',
      timestamp: new Date(new Date().setHours(15, 15, 0, 0)),
      isPassed: new Date().getHours() > 15 || (new Date().getHours() === 15 && new Date().getMinutes() > 15),
    },
    {
      name: 'Maghrib',
      nameAr: 'المغرب',
      time: '17:35',
      timestamp: new Date(new Date().setHours(17, 35, 0, 0)),
      isPassed: new Date().getHours() > 17 || (new Date().getHours() === 17 && new Date().getMinutes() > 35),
    },
    {
      name: 'Isha',
      nameAr: 'العشاء',
      time: '19:05',
      timestamp: new Date(new Date().setHours(19, 5, 0, 0)),
      isPassed: new Date().getHours() > 19 || (new Date().getHours() === 19 && new Date().getMinutes() > 5),
    },
  ],
};

// Calculate next prayer
mockPrayerTimes.nextPrayer = mockPrayerTimes.times.find(prayer => !prayer.isPassed);

interface PrayerTimeWidgetProps {
  onOptimalTimeSelect?: (time: Date, prayerName: string) => void;
  selectedDate?: Date;
  showSchedulingTips?: boolean;
}

export const PrayerTimeWidget: React.FC<PrayerTimeWidgetProps> = ({
  onOptimalTimeSelect,
  selectedDate = new Date(),
  showSchedulingTips = true,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const [prayerData, setPrayerData] = useState<PrayerTimesData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Mock API call - replace with actual prayer times service
  useEffect(() => {
    const fetchPrayerTimes = async () => {
      setIsLoading(true);
      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        setPrayerData(mockPrayerTimes);
        setError(null);
      } catch (err) {
        setError(language === 'ar' ? 'خطأ في تحميل مواقيت الصلاة' : 'Error loading prayer times');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPrayerTimes();
  }, [selectedDate, language]);

  const handleRefresh = () => {
    setPrayerData(null);
    setIsLoading(true);
    // Trigger refetch
    setTimeout(() => {
      setPrayerData(mockPrayerTimes);
      setIsLoading(false);
    }, 1000);
  };

  const getOptimalPostingTime = (prayerTime: PrayerTime) => {
    // Suggest posting 30 minutes after prayer time for better engagement
    const optimalTime = new Date(prayerTime.timestamp);
    optimalTime.setMinutes(optimalTime.getMinutes() + 30);
    return optimalTime;
  };

  const formatDateHeader = (date: Date) => {
    if (isToday(date)) {
      return language === 'ar' ? 'اليوم' : 'Today';
    }
    if (isTomorrow(date)) {
      return language === 'ar' ? 'غداً' : 'Tomorrow';
    }
    return format(date, 'EEEE, MMM dd', { locale: language === 'ar' ? ar : enUS });
  };

  if (isLoading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={language === 'ar' ? 'مواقيت الصلاة' : 'Prayer Times'}
          avatar={<AccessTime />}
        />
        <CardContent>
          <LoadingSpinner size="small" message={language === 'ar' ? 'جارٍ التحميل...' : 'Loading...'} />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={language === 'ar' ? 'مواقيت الصلاة' : 'Prayer Times'}
          avatar={<AccessTime />}
          action={
            <IconButton onClick={handleRefresh}>
              <Refresh />
            </IconButton>
          }
        />
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title={language === 'ar' ? 'مواقيت الصلاة' : 'Prayer Times'}
        avatar={<AccessTime />}
        action={
          <IconButton onClick={handleRefresh} size="small">
            <Refresh />
          </IconButton>
        }
        subheader={
          <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
            <LocationOn fontSize="small" />
            <Typography variant="body2">
              {prayerData?.location}
            </Typography>
          </Box>
        }
      />
      
      <CardContent sx={{ pt: 0 }}>
        {/* Date */}
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <CalendarToday fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            {formatDateHeader(selectedDate)}
          </Typography>
        </Box>

        {/* Next Prayer Highlight */}
        {prayerData?.nextPrayer && (
          <Alert 
            severity="info" 
            sx={{ mb: 2 }}
            icon={<Schedule />}
          >
            <Typography variant="body2">
              <strong>
                {language === 'ar' ? 'الصلاة القادمة: ' : 'Next Prayer: '}
                {language === 'ar' 
                  ? prayerData.nextPrayer.nameAr 
                  : prayerData.nextPrayer.name
                }
              </strong>
              <br />
              {prayerData.nextPrayer.time}
            </Typography>
          </Alert>
        )}

        {/* Prayer Times List */}
        <List dense sx={{ p: 0 }}>
          {prayerData?.times.map((prayer) => (
            <ListItem
              key={prayer.name}
              sx={{
                px: 0,
                py: 0.5,
                opacity: prayer.isPassed ? 0.6 : 1,
                backgroundColor: prayer === prayerData.nextPrayer 
                  ? theme.palette.primary.main + '10' 
                  : 'transparent',
                borderRadius: 1,
                mb: 0.5,
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <AccessTime 
                  fontSize="small" 
                  color={prayer.isPassed ? 'disabled' : 'action'} 
                />
              </ListItemIcon>
              <ListItemText
                primary={
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontWeight: prayer === prayerData.nextPrayer ? 600 : 400,
                      color: prayer.isPassed ? 'text.disabled' : 'text.primary'
                    }}
                  >
                    {language === 'ar' ? prayer.nameAr : prayer.name}
                  </Typography>
                }
                secondary={prayer.time}
              />
              {onOptimalTimeSelect && !prayer.isPassed && (
                <Tooltip 
                  title={language === 'ar' 
                    ? 'اقتراح وقت مثالي للنشر' 
                    : 'Suggest optimal posting time'
                  }
                >
                  <IconButton
                    size="small"
                    onClick={() => onOptimalTimeSelect(
                      getOptimalPostingTime(prayer), 
                      prayer.name
                    )}
                  >
                    <Schedule fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </ListItem>
          ))}
        </List>

        {/* Scheduling Tips */}
        {showSchedulingTips && (
          <Box mt={2}>
            <Box display="flex" alignItems="center" gap={0.5} mb={1}>
              <Info fontSize="small" color="action" />
              <Typography variant="caption" color="text.secondary">
                {language === 'ar' ? 'نصائح الجدولة' : 'Scheduling Tips'}
              </Typography>
            </Box>
            <Typography variant="caption" color="text.secondary" display="block">
              {language === 'ar'
                ? 'أفضل أوقات النشر: بعد صلاة المغرب (٦-٨ مساءً) وبعد صلاة العشاء (٩-١١ مساءً)'
                : 'Best posting times: After Maghrib (6-8 PM) and after Isha (9-11 PM) for higher engagement'
              }
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};