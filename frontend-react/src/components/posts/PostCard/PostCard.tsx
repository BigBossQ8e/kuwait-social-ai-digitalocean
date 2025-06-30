// Post card component for grid and list views

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Typography,
  Box,
  Chip,
  IconButton,
  Button,
  Menu,
  MenuItem,
  Divider,
  Stack,
  Checkbox,
  Tooltip,
  Avatar,
  AvatarGroup,
  useTheme,
  alpha,
} from '@mui/material';
import {
  MoreVert,
  Edit,
  Delete,
  FileCopy,
  Send,
  Schedule,
  CheckCircle,
  Error,
  Drafts,
  Instagram,
  Twitter,
  CameraAlt,
  FavoriteBorder,
  ChatBubbleOutline,
  Share,
  CalendarMonth,
  Tag,
} from '@mui/icons-material';
import { format, formatDistanceToNow } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { PLATFORM_LABELS } from '../../../utils/constants';
import type { Post } from '../../../types/api.types';

interface PostCardProps {
  post: Post;
  onEdit?: (post: Post) => void;
  onDelete?: (postId: number) => void;
  onPublish?: (postId: number) => void;
  onDuplicate?: (post: Post) => void;
  selected?: boolean;
  onSelect?: () => void;
  variant?: 'grid' | 'list';
}

const statusConfig = {
  published: {
    icon: <CheckCircle fontSize="small" />,
    color: 'success' as const,
    label: 'Published',
    labelAr: 'منشور',
  },
  scheduled: {
    icon: <Schedule fontSize="small" />,
    color: 'info' as const,
    label: 'Scheduled',
    labelAr: 'مجدول',
  },
  draft: {
    icon: <Drafts fontSize="small" />,
    color: 'default' as const,
    label: 'Draft',
    labelAr: 'مسودة',
  },
  failed: {
    icon: <Error fontSize="small" />,
    color: 'error' as const,
    label: 'Failed',
    labelAr: 'فشل',
  },
};

const platformIcons: Record<string, React.ReactNode> = {
  instagram: <Instagram fontSize="small" />,
  twitter: <Twitter fontSize="small" />,
  snapchat: <CameraAlt fontSize="small" />,
};

export const PostCard: React.FC<PostCardProps> = ({
  post,
  onEdit,
  onDelete,
  onPublish,
  onDuplicate,
  selected = false,
  onSelect,
  variant = 'grid',
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const locale = language === 'ar' ? ar : enUS;

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAction = (action: () => void) => {
    action();
    handleMenuClose();
  };

  const formatDate = (date: string | Date) => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return format(dateObj, 'PPp', { locale });
  };

  const getRelativeTime = (date: string | Date) => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true, locale });
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const renderEngagement = () => {
    if (!post.metrics) return null;
    
    const { likes = 0, comments = 0, shares = 0 } = post.metrics;
    const total = likes + comments + shares;
    
    if (total === 0) return null;
    
    return (
      <Box display="flex" gap={1.5} alignItems="center">
        <Tooltip title={language === 'ar' ? 'إعجابات' : 'Likes'}>
          <Box display="flex" alignItems="center" gap={0.5}>
            <FavoriteBorder fontSize="small" color="action" />
            <Typography variant="caption">{likes}</Typography>
          </Box>
        </Tooltip>
        <Tooltip title={language === 'ar' ? 'تعليقات' : 'Comments'}>
          <Box display="flex" alignItems="center" gap={0.5}>
            <ChatBubbleOutline fontSize="small" color="action" />
            <Typography variant="caption">{comments}</Typography>
          </Box>
        </Tooltip>
        <Tooltip title={language === 'ar' ? 'مشاركات' : 'Shares'}>
          <Box display="flex" alignItems="center" gap={0.5}>
            <Share fontSize="small" color="action" />
            <Typography variant="caption">{shares}</Typography>
          </Box>
        </Tooltip>
      </Box>
    );
  };

  if (variant === 'list') {
    return (
      <Card 
        sx={{ 
          position: 'relative',
          transition: 'all 0.2s',
          border: selected ? `2px solid ${theme.palette.primary.main}` : 'none',
          backgroundColor: selected ? alpha(theme.palette.primary.main, 0.05) : 'inherit',
        }}
      >
        <CardContent>
          <Box display="flex" gap={2}>
            {/* Checkbox */}
            {onSelect && (
              <Checkbox
                checked={selected}
                onChange={onSelect}
                onClick={(e) => e.stopPropagation()}
              />
            )}

            {/* Media Preview */}
            {post.media_files && post.media_files.length > 0 && (
              <Box
                component="img"
                src={post.media_files[0].url}
                alt="Post media"
                sx={{
                  width: 120,
                  height: 80,
                  objectFit: 'cover',
                  borderRadius: 1,
                }}
              />
            )}

            {/* Content */}
            <Box flex={1}>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <Box>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    {/* Status */}
                    <Chip
                      icon={statusConfig[post.status as keyof typeof statusConfig]?.icon}
                      label={language === 'ar' 
                        ? statusConfig[post.status as keyof typeof statusConfig]?.labelAr 
                        : statusConfig[post.status as keyof typeof statusConfig]?.label
                      }
                      size="small"
                      color={statusConfig[post.status as keyof typeof statusConfig]?.color}
                    />
                    
                    {/* Platforms */}
                    <AvatarGroup max={3} sx={{ '& .MuiAvatar-root': { width: 24, height: 24 } }}>
                      {post.platform?.map(platform => (
                        <Avatar key={platform} sx={{ bgcolor: 'background.paper' }}>
                          {platformIcons[platform]}
                        </Avatar>
                      ))}
                    </AvatarGroup>
                    
                    {/* Date */}
                    <Typography variant="caption" color="text.secondary">
                      {post.status === 'scheduled' && post.scheduled_time
                        ? formatDate(post.scheduled_time)
                        : getRelativeTime(post.created_at || new Date())
                      }
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    {truncateText(post.caption || '', 150)}
                  </Typography>
                  
                  <Box display="flex" gap={1} flexWrap="wrap">
                    {post.hashtags?.slice(0, 3).map((tag, index) => (
                      <Chip
                        key={index}
                        label={tag}
                        size="small"
                        variant="outlined"
                        icon={<Tag fontSize="small" />}
                      />
                    ))}
                    {post.hashtags && post.hashtags.length > 3 && (
                      <Chip
                        label={`+${post.hashtags.length - 3}`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </Box>
                
                {/* Actions */}
                <IconButton size="small" onClick={handleMenuOpen}>
                  <MoreVert />
                </IconButton>
              </Box>
              
              {/* Engagement Metrics */}
              <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                {renderEngagement()}
                
                <Box display="flex" gap={1}>
                  {post.status === 'draft' && onPublish && (
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() => onPublish(post.id)}
                      startIcon={<Send fontSize="small" />}
                    >
                      {language === 'ar' ? 'نشر' : 'Publish'}
                    </Button>
                  )}
                  {onEdit && (
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => onEdit(post)}
                      startIcon={<Edit fontSize="small" />}
                    >
                      {language === 'ar' ? 'تعديل' : 'Edit'}
                    </Button>
                  )}
                </Box>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Grid variant
  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        transition: 'all 0.2s',
        border: selected ? `2px solid ${theme.palette.primary.main}` : 'none',
        backgroundColor: selected ? alpha(theme.palette.primary.main, 0.05) : 'inherit',
        '&:hover': {
          boxShadow: theme.shadows[4],
        },
      }}
    >
      {/* Checkbox */}
      {onSelect && (
        <Box position="absolute" top={8} left={8} zIndex={1}>
          <Checkbox
            checked={selected}
            onChange={onSelect}
            onClick={(e) => e.stopPropagation()}
            sx={{
              backgroundColor: 'background.paper',
              borderRadius: 1,
              '&:hover': {
                backgroundColor: 'background.paper',
              },
            }}
          />
        </Box>
      )}

      {/* Media */}
      {post.media_files && post.media_files.length > 0 ? (
        <CardMedia
          component="img"
          height="200"
          image={post.media_files[0].url}
          alt="Post media"
          sx={{ objectFit: 'cover' }}
        />
      ) : (
        <Box
          sx={{
            height: 200,
            backgroundColor: theme.palette.grey[100],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography variant="h1" sx={{ opacity: 0.1 }}>
            {post.caption?.[0]?.toUpperCase() || '?'}
          </Typography>
        </Box>
      )}

      <CardContent sx={{ flex: 1 }}>
        {/* Status and Platforms */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Chip
            icon={statusConfig[post.status as keyof typeof statusConfig]?.icon}
            label={language === 'ar' 
              ? statusConfig[post.status as keyof typeof statusConfig]?.labelAr 
              : statusConfig[post.status as keyof typeof statusConfig]?.label
            }
            size="small"
            color={statusConfig[post.status as keyof typeof statusConfig]?.color}
          />
          
          <AvatarGroup max={3} sx={{ '& .MuiAvatar-root': { width: 24, height: 24 } }}>
            {post.platform?.map(platform => (
              <Avatar key={platform} sx={{ bgcolor: 'background.paper' }}>
                {platformIcons[platform]}
              </Avatar>
            ))}
          </AvatarGroup>
        </Box>

        {/* Caption */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {truncateText(post.caption || '', 100)}
        </Typography>

        {/* Hashtags */}
        {post.hashtags && post.hashtags.length > 0 && (
          <Box display="flex" gap={0.5} flexWrap="wrap" mb={2}>
            {post.hashtags.slice(0, 2).map((tag, index) => (
              <Chip
                key={index}
                label={tag}
                size="small"
                variant="outlined"
              />
            ))}
            {post.hashtags.length > 2 && (
              <Chip
                label={`+${post.hashtags.length - 2}`}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        )}

        {/* Date */}
        <Box display="flex" alignItems="center" gap={0.5}>
          <CalendarMonth fontSize="small" color="action" />
          <Typography variant="caption" color="text.secondary">
            {post.status === 'scheduled' && post.scheduled_time
              ? formatDate(post.scheduled_time)
              : getRelativeTime(post.created_at || new Date())
            }
          </Typography>
        </Box>
      </CardContent>

      {/* Engagement Metrics */}
      {post.metrics && (
        <Box px={2} pb={1}>
          <Divider sx={{ mb: 1 }} />
          {renderEngagement()}
        </Box>
      )}

      <CardActions sx={{ justifyContent: 'space-between' }}>
        <Box>
          {post.status === 'draft' && onPublish && (
            <Button
              size="small"
              onClick={() => onPublish(post.id)}
              startIcon={<Send fontSize="small" />}
            >
              {language === 'ar' ? 'نشر' : 'Publish'}
            </Button>
          )}
        </Box>
        
        <IconButton size="small" onClick={handleMenuOpen}>
          <MoreVert />
        </IconButton>
      </CardActions>

      {/* Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        {onEdit && (
          <MenuItem onClick={() => handleAction(() => onEdit(post))}>
            <Edit fontSize="small" sx={{ mr: 1 }} />
            {language === 'ar' ? 'تعديل' : 'Edit'}
          </MenuItem>
        )}
        
        {onDuplicate && (
          <MenuItem onClick={() => handleAction(() => onDuplicate(post))}>
            <FileCopy fontSize="small" sx={{ mr: 1 }} />
            {language === 'ar' ? 'نسخ' : 'Duplicate'}
          </MenuItem>
        )}
        
        {post.status === 'scheduled' && onPublish && (
          <MenuItem onClick={() => handleAction(() => onPublish(post.id))}>
            <Send fontSize="small" sx={{ mr: 1 }} />
            {language === 'ar' ? 'نشر الآن' : 'Publish Now'}
          </MenuItem>
        )}
        
        <Divider />
        
        {onDelete && (
          <MenuItem 
            onClick={() => handleAction(() => onDelete(post.id))}
            sx={{ color: 'error.main' }}
          >
            <Delete fontSize="small" sx={{ mr: 1 }} />
            {language === 'ar' ? 'حذف' : 'Delete'}
          </MenuItem>
        )}
      </Menu>
    </Card>
  );
};