// Recent activity feed component

import React from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Typography,
  Chip,
  useTheme,
  Button,
} from '@mui/material';
import {
  PostAdd,
  TrendingUp,
  Schedule,
  Analytics,
  Instagram,
  Twitter,
  CameraAlt,
  MoreHoriz,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';

interface Activity {
  id: string;
  type: 'post_published' | 'engagement' | 'schedule' | 'competitor' | 'comment' | 'mention';
  title: string;
  description: string;
  timestamp: Date;
  platform: 'instagram' | 'snapchat' | 'twitter' | 'multiple' | 'analysis';
  metadata?: {
    likes?: number;
    comments?: number;
    shares?: number;
    engagement_rate?: number;
  };
}

interface RecentActivityProps {
  activities: Activity[];
  maxItems?: number;
  showMore?: boolean;
  onShowMore?: () => void;
}

const getActivityIcon = (type: string, platform: string) => {
  switch (type) {
    case 'post_published':
      return <PostAdd />;
    case 'engagement':
      return <TrendingUp />;
    case 'schedule':
      return <Schedule />;
    case 'competitor':
      return <Analytics />;
    case 'comment':
    case 'mention':
      return <CameraAlt />;
    default:
      return <PostAdd />;
  }
};

const getPlatformIcon = (platform: string) => {
  switch (platform) {
    case 'instagram':
      return <Instagram fontSize="small" />;
    case 'twitter':
      return <Twitter fontSize="small" />;
    case 'snapchat':
      return <CameraAlt fontSize="small" />;
    default:
      return null;
  }
};

const getActivityColor = (type: string) => {
  switch (type) {
    case 'post_published':
      return 'success';
    case 'engagement':
      return 'primary';
    case 'schedule':
      return 'warning';
    case 'competitor':
      return 'info';
    case 'comment':
    case 'mention':
      return 'secondary';
    default:
      return 'default';
  }
};

export const RecentActivity: React.FC<RecentActivityProps> = ({
  activities,
  maxItems = 5,
  showMore = true,
  onShowMore,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  
  const displayedActivities = activities.slice(0, maxItems);
  const hasMore = activities.length > maxItems;

  const formatTimeAgo = (date: Date) => {
    return formatDistanceToNow(date, {
      addSuffix: true,
      locale: language === 'ar' ? ar : enUS,
    });
  };

  if (activities.length === 0) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        py={4}
        textAlign="center"
      >
        <Analytics sx={{ fontSize: 48, color: theme.palette.grey[400], mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {language === 'ar' ? 'لا توجد أنشطة حديثة' : 'No recent activity'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {language === 'ar' 
            ? 'ستظهر أنشطتك الأخيرة هنا'
            : 'Your recent activities will appear here'
          }
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <List sx={{ p: 0 }}>
        {displayedActivities.map((activity, index) => (
          <ListItem
            key={activity.id}
            sx={{
              px: 0,
              py: 1.5,
              borderBottom: index < displayedActivities.length - 1 
                ? `1px solid ${theme.palette.divider}` 
                : 'none',
            }}
          >
            <ListItemAvatar>
              <Avatar
                sx={{
                  backgroundColor: theme.palette[getActivityColor(activity.type) as keyof typeof theme.palette]?.main || theme.palette.primary.main,
                  color: 'white',
                  width: 40,
                  height: 40,
                }}
              >
                {getActivityIcon(activity.type, activity.platform)}
              </Avatar>
            </ListItemAvatar>
            
            <ListItemText
              primary={
                <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {activity.title}
                  </Typography>
                  {activity.platform !== 'multiple' && activity.platform !== 'analysis' && (
                    <Box display="flex" alignItems="center">
                      {getPlatformIcon(activity.platform)}
                    </Box>
                  )}
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {activity.description}
                  </Typography>
                  
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="caption" color="text.secondary">
                      {formatTimeAgo(activity.timestamp)}
                    </Typography>
                    
                    {activity.metadata && (
                      <Box display="flex" gap={1}>
                        {activity.metadata.likes && (
                          <Chip
                            label={`${activity.metadata.likes} ${language === 'ar' ? 'إعجاب' : 'likes'}`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                        {activity.metadata.engagement_rate && (
                          <Chip
                            label={`${activity.metadata.engagement_rate}% ${language === 'ar' ? 'تفاعل' : 'engagement'}`}
                            size="small"
                            variant="outlined"
                            color="primary"
                          />
                        )}
                      </Box>
                    )}
                  </Box>
                </Box>
              }
            />
          </ListItem>
        ))}
      </List>
      
      {hasMore && showMore && (
        <Box display="flex" justifyContent="center" mt={2}>
          <Button
            variant="outlined"
            startIcon={<MoreHoriz />}
            onClick={onShowMore}
            size="small"
          >
            {language === 'ar' ? 'عرض المزيد' : 'Show More'}
          </Button>
        </Box>
      )}
    </Box>
  );
};

// Activity item skeleton for loading states
export const ActivitySkeleton: React.FC = () => {
  const theme = useTheme();
  
  return (
    <List sx={{ p: 0 }}>
      {[1, 2, 3, 4, 5].map((item) => (
        <ListItem key={item} sx={{ px: 0, py: 1.5 }}>
          <ListItemAvatar>
            <Box
              sx={{
                width: 40,
                height: 40,
                backgroundColor: theme.palette.grey[300],
                borderRadius: '50%',
              }}
            />
          </ListItemAvatar>
          <ListItemText
            primary={
              <Box mb={0.5}>
                <Box
                  sx={{
                    height: 16,
                    backgroundColor: theme.palette.grey[300],
                    borderRadius: 1,
                    width: '60%',
                  }}
                />
              </Box>
            }
            secondary={
              <Box>
                <Box
                  sx={{
                    height: 14,
                    backgroundColor: theme.palette.grey[300],
                    borderRadius: 1,
                    width: '90%',
                    mb: 1,
                  }}
                />
                <Box
                  sx={{
                    height: 12,
                    backgroundColor: theme.palette.grey[300],
                    borderRadius: 1,
                    width: '40%',
                  }}
                />
              </Box>
            }
          />
        </ListItem>
      ))}
    </List>
  );
};