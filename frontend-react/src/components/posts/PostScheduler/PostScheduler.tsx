// Post scheduling calendar interface

import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Chip,
  Avatar,
  AvatarGroup,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Badge,
  Tooltip,
  useTheme,
  alpha,
  Stack,
  TextField,
  Alert,
} from '@mui/material';
import {
  ChevronLeft,
  ChevronRight,
  Today,
  Add,
  Schedule,
  Instagram,
  Twitter,
  CameraAlt,
  Edit,
  Delete,
  ContentCopy,
  Close,
  CalendarMonth,
} from '@mui/icons-material';
import {
  format,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isSameMonth,
  isSameDay,
  isToday,
  addMonths,
  subMonths,
  getDay,
  startOfWeek,
  endOfWeek,
  setHours,
  setMinutes,
  isBefore,
} from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { PostEditor } from '../PostEditor';
import type { Post, PostDraft } from '../../../types/api.types';

interface PostSchedulerProps {
  posts: Post[];
  onSchedulePost?: (post: PostDraft, scheduledTime: string) => void;
  onUpdatePost?: (postId: number, scheduledTime: string) => void;
  onDeletePost?: (postId: number) => void;
  onDuplicatePost?: (post: Post, newTime: string) => void;
}

interface TimeSlot {
  time: string;
  label: string;
  labelAr: string;
  recommended?: boolean;
}

const timeSlots: TimeSlot[] = [
  { time: '08:00', label: '8:00 AM', labelAr: '٨:٠٠ ص' },
  { time: '10:00', label: '10:00 AM', labelAr: '١٠:٠٠ ص' },
  { time: '12:00', label: '12:00 PM', labelAr: '١٢:٠٠ م' },
  { time: '14:00', label: '2:00 PM', labelAr: '٢:٠٠ م' },
  { time: '16:00', label: '4:00 PM', labelAr: '٤:٠٠ م' },
  { time: '18:00', label: '6:00 PM', labelAr: '٦:٠٠ م', recommended: true },
  { time: '20:00', label: '8:00 PM', labelAr: '٨:٠٠ م', recommended: true },
  { time: '21:00', label: '9:00 PM', labelAr: '٩:٠٠ م', recommended: true },
  { time: '22:00', label: '10:00 PM', labelAr: '١٠:٠٠ م' },
];

const platformIcons: Record<string, React.ReactNode> = {
  instagram: <Instagram fontSize="small" />,
  twitter: <Twitter fontSize="small" />,
  snapchat: <CameraAlt fontSize="small" />,
};

const platformColors: Record<string, string> = {
  instagram: '#E4405F',
  twitter: '#1DA1F2',
  snapchat: '#FFFC00',
};

export const PostScheduler: React.FC<PostSchedulerProps> = ({
  posts,
  onSchedulePost,
  onUpdatePost,
  onDeletePost,
  onDuplicatePost,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const locale = language === 'ar' ? ar : enUS;
  
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [showPostEditor, setShowPostEditor] = useState(false);
  const [showTimeSlotDialog, setShowTimeSlotDialog] = useState(false);
  const [customTime, setCustomTime] = useState('');

  // Get scheduled posts for a specific date
  const getPostsForDate = (date: Date) => {
    return posts.filter(post => {
      if (post.status !== 'scheduled' || !post.scheduled_time) return false;
      const postDate = new Date(post.scheduled_time);
      return isSameDay(postDate, date);
    });
  };

  // Generate calendar days
  const calendarDays = useMemo(() => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(currentMonth);
    const calendarStart = startOfWeek(monthStart, { locale });
    const calendarEnd = endOfWeek(monthEnd, { locale });
    
    return eachDayOfInterval({ start: calendarStart, end: calendarEnd });
  }, [currentMonth, locale]);

  // Get week days
  const weekDays = useMemo(() => {
    const days = language === 'ar' 
      ? ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
      : ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    
    // Reorder based on locale's first day of week
    const firstDayOfWeek = locale.options?.weekStartsOn || 0;
    return [...days.slice(firstDayOfWeek), ...days.slice(0, firstDayOfWeek)];
  }, [language, locale]);

  const handlePreviousMonth = () => {
    setCurrentMonth(subMonths(currentMonth, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(addMonths(currentMonth, 1));
  };

  const handleToday = () => {
    setCurrentMonth(new Date());
    setSelectedDate(new Date());
  };

  const handleDateClick = (date: Date) => {
    if (isBefore(date, new Date()) && !isSameDay(date, new Date())) {
      return; // Don't allow selecting past dates
    }
    setSelectedDate(date);
  };

  const handleScheduleNewPost = () => {
    if (!selectedDate) return;
    setShowTimeSlotDialog(true);
  };

  const handleTimeSlotSelect = (time: string) => {
    if (!selectedDate) return;
    
    const [hours, minutes] = time.split(':').map(Number);
    const scheduledTime = setMinutes(setHours(selectedDate, hours), minutes);
    
    setShowTimeSlotDialog(false);
    setShowPostEditor(true);
  };

  const handleSavePost = (post: PostDraft, action: 'save' | 'schedule' | 'publish') => {
    if (!selectedDate || !customTime) return;
    
    const [hours, minutes] = customTime.split(':').map(Number);
    const scheduledTime = setMinutes(setHours(selectedDate, hours), minutes);
    
    onSchedulePost?.(post, scheduledTime.toISOString());
    setShowPostEditor(false);
    setCustomTime('');
  };

  const handleReschedulePost = (post: Post, newTime: string) => {
    if (!selectedDate) return;
    
    const [hours, minutes] = newTime.split(':').map(Number);
    const scheduledTime = setMinutes(setHours(selectedDate, hours), minutes);
    
    onUpdatePost?.(post.id, scheduledTime.toISOString());
  };

  const handleDuplicatePost = (post: Post) => {
    if (!selectedDate) return;
    setSelectedPost(post);
    setShowTimeSlotDialog(true);
  };

  const renderCalendarDay = (date: Date) => {
    const dayPosts = getPostsForDate(date);
    const isCurrentMonth = isSameMonth(date, currentMonth);
    const isSelectedDate = selectedDate && isSameDay(date, selectedDate);
    const isPastDate = isBefore(date, new Date()) && !isSameDay(date, new Date());
    
    return (
      <Box
        key={date.toISOString()}
        onClick={() => handleDateClick(date)}
        sx={{
          aspectRatio: '1',
          p: 1,
          border: `1px solid ${theme.palette.divider}`,
          cursor: isPastDate ? 'not-allowed' : 'pointer',
          backgroundColor: isSelectedDate 
            ? alpha(theme.palette.primary.main, 0.1)
            : isToday(date)
            ? alpha(theme.palette.info.main, 0.05)
            : 'transparent',
          opacity: !isCurrentMonth || isPastDate ? 0.5 : 1,
          '&:hover': {
            backgroundColor: isPastDate 
              ? 'transparent'
              : alpha(theme.palette.primary.main, 0.05),
          },
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Date number */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Typography
            variant="body2"
            fontWeight={isToday(date) ? 'bold' : 'normal'}
            color={isToday(date) ? 'primary' : 'textPrimary'}
          >
            {format(date, 'd', { locale })}
          </Typography>
          
          {dayPosts.length > 0 && (
            <Badge badgeContent={dayPosts.length} color="primary" />
          )}
        </Box>
        
        {/* Post indicators */}
        {dayPosts.length > 0 && (
          <Box mt={0.5}>
            <AvatarGroup 
              max={3} 
              sx={{ 
                justifyContent: 'flex-start',
                '& .MuiAvatar-root': { 
                  width: 20, 
                  height: 20,
                  fontSize: '0.75rem',
                  border: 'none',
                },
              }}
            >
              {dayPosts.map((post, index) => (
                <Avatar
                  key={index}
                  sx={{ 
                    bgcolor: platformColors[post.platform?.[0] || 'instagram'] || '#E4405F',
                  }}
                >
                  {platformIcons[post.platform?.[0] || 'instagram']}
                </Avatar>
              ))}
            </AvatarGroup>
          </Box>
        )}
      </Box>
    );
  };

  const renderPostsList = () => {
    if (!selectedDate) return null;
    
    const dayPosts = getPostsForDate(selectedDate);
    const sortedPosts = [...dayPosts].sort((a, b) => {
      const timeA = new Date(a.scheduled_time || 0).getTime();
      const timeB = new Date(b.scheduled_time || 0).getTime();
      return timeA - timeB;
    });
    
    return (
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            {format(selectedDate, 'PPPP', { locale })}
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleScheduleNewPost}
            disabled={isBefore(selectedDate, new Date()) && !isSameDay(selectedDate, new Date())}
          >
            {language === 'ar' ? 'جدولة منشور' : 'Schedule Post'}
          </Button>
        </Box>
        
        {sortedPosts.length === 0 ? (
          <Alert severity="info">
            {language === 'ar' 
              ? 'لا توجد منشورات مجدولة لهذا اليوم'
              : 'No posts scheduled for this day'
            }
          </Alert>
        ) : (
          <List>
            {sortedPosts.map((post) => (
              <ListItem
                key={post.id}
                sx={{
                  border: `1px solid ${theme.palette.divider}`,
                  borderRadius: 1,
                  mb: 1,
                }}
              >
                <ListItemAvatar>
                  <AvatarGroup max={2} sx={{ '& .MuiAvatar-root': { width: 32, height: 32 } }}>
                    {post.platform?.map(platform => (
                      <Avatar
                        key={platform}
                        sx={{ bgcolor: platformColors[platform] }}
                      >
                        {platformIcons[platform]}
                      </Avatar>
                    ))}
                  </AvatarGroup>
                </ListItemAvatar>
                
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip
                        icon={<Schedule />}
                        label={format(new Date(post.scheduled_time!), 'p', { locale })}
                        size="small"
                        color="primary"
                      />
                      <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                        {post.caption}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    post.hashtags && post.hashtags.length > 0 
                      ? post.hashtags.slice(0, 3).join(' ') 
                      : undefined
                  }
                />
                
                <ListItemSecondaryAction>
                  <Stack direction="row" spacing={1}>
                    <Tooltip title={language === 'ar' ? 'تعديل' : 'Edit'}>
                      <IconButton size="small">
                        <Edit fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={language === 'ar' ? 'نسخ' : 'Duplicate'}>
                      <IconButton 
                        size="small"
                        onClick={() => handleDuplicatePost(post)}
                      >
                        <ContentCopy fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={language === 'ar' ? 'حذف' : 'Delete'}>
                      <IconButton 
                        size="small"
                        onClick={() => onDeletePost?.(post.id)}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    );
  };

  return (
    <Box>
      <Paper sx={{ p: 3 }}>
        {/* Calendar Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box display="flex" alignItems="center" gap={2}>
            <IconButton onClick={handlePreviousMonth}>
              {language === 'ar' ? <ChevronRight /> : <ChevronLeft />}
            </IconButton>
            <Typography variant="h5">
              {format(currentMonth, 'MMMM yyyy', { locale })}
            </Typography>
            <IconButton onClick={handleNextMonth}>
              {language === 'ar' ? <ChevronLeft /> : <ChevronRight />}
            </IconButton>
          </Box>
          
          <Button
            startIcon={<Today />}
            onClick={handleToday}
          >
            {language === 'ar' ? 'اليوم' : 'Today'}
          </Button>
        </Box>
        
        {/* Calendar Grid */}
        <Box>
          {/* Week days header */}
          <Box
            display="grid"
            gridTemplateColumns="repeat(7, 1fr)"
            gap={0}
            mb={1}
          >
            {weekDays.map(day => (
              <Box
                key={day}
                textAlign="center"
                py={1}
                sx={{
                  backgroundColor: theme.palette.grey[100],
                  fontWeight: 'bold',
                }}
              >
                <Typography variant="caption">
                  {day}
                </Typography>
              </Box>
            ))}
          </Box>
          
          {/* Calendar days */}
          <Box
            display="grid"
            gridTemplateColumns="repeat(7, 1fr)"
            gap={0}
          >
            {calendarDays.map(renderCalendarDay)}
          </Box>
        </Box>
        
        {/* Selected date posts */}
        {selectedDate && (
          <Box mt={4}>
            <Divider sx={{ mb: 3 }} />
            {renderPostsList()}
          </Box>
        )}
      </Paper>
      
      {/* Time Slot Selection Dialog */}
      <Dialog
        open={showTimeSlotDialog}
        onClose={() => setShowTimeSlotDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {language === 'ar' ? 'اختر وقت النشر' : 'Select Post Time'}
            </Typography>
            <IconButton onClick={() => setShowTimeSlotDialog(false)} size="small">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {language === 'ar' 
              ? `التاريخ: ${format(selectedDate || new Date(), 'PPP', { locale })}`
              : `Date: ${format(selectedDate || new Date(), 'PPP', { locale })}`
            }
          </Typography>
          
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              {language === 'ar' ? 'الأوقات المقترحة' : 'Suggested Times'}
            </Typography>
            
            <Box display="grid" gridTemplateColumns="repeat(3, 1fr)" gap={1} mt={1}>
              {timeSlots.map(slot => (
                <Button
                  key={slot.time}
                  variant={slot.recommended ? 'contained' : 'outlined'}
                  onClick={() => handleTimeSlotSelect(slot.time)}
                  sx={{
                    justifyContent: 'center',
                    ...(slot.recommended && {
                      backgroundColor: theme.palette.success.main,
                      '&:hover': {
                        backgroundColor: theme.palette.success.dark,
                      },
                    }),
                  }}
                >
                  {language === 'ar' ? slot.labelAr : slot.label}
                </Button>
              ))}
            </Box>
            
            <Box mt={3}>
              <Typography variant="subtitle2" gutterBottom>
                {language === 'ar' ? 'وقت مخصص' : 'Custom Time'}
              </Typography>
              <TextField
                type="time"
                value={customTime}
                onChange={(e) => setCustomTime(e.target.value)}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Box>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setShowTimeSlotDialog(false)}>
            {language === 'ar' ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button
            variant="contained"
            onClick={() => customTime && handleTimeSlotSelect(customTime)}
            disabled={!customTime}
          >
            {language === 'ar' ? 'تأكيد' : 'Confirm'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Post Editor Dialog */}
      <Dialog
        open={showPostEditor}
        onClose={() => setShowPostEditor(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent>
          <PostEditor
            initialData={selectedPost ? { ...selectedPost } : undefined}
            onSave={handleSavePost}
            onCancel={() => setShowPostEditor(false)}
          />
        </DialogContent>
      </Dialog>
    </Box>
  );
};