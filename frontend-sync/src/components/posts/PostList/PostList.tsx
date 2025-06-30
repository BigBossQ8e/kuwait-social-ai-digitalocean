// Post list component with filtering and pagination

import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Button,
  InputAdornment,
  ToggleButton,
  ToggleButtonGroup,
  Pagination,
  Stack,
  CircularProgress,
  Alert,
  Menu,
  IconButton,
  Checkbox,
  ListItemText,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Search,
  FilterList,
  ViewList,
  ViewModule,
  CalendarMonth,
  Schedule,
  CheckCircle,
  Error,
  Drafts,
  MoreVert,
  Instagram,
  Twitter,
  CameraAlt,
} from '@mui/icons-material';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { PostCard } from '../PostCard';
import { PLATFORMS, PLATFORM_LABELS } from '../../../utils/constants';
import type { Post } from '../../../types/api.types';

interface PostListProps {
  posts: Post[];
  loading?: boolean;
  error?: string | null;
  onEdit?: (post: Post) => void;
  onDelete?: (postId: number) => void;
  onPublish?: (postId: number) => void;
  onDuplicate?: (post: Post) => void;
  onBulkAction?: (action: string, postIds: number[]) => void;
}

type PostStatus = 'all' | 'published' | 'scheduled' | 'draft' | 'failed';
type ViewMode = 'grid' | 'list';

const statusOptions: { value: PostStatus; label: string; labelAr: string; icon: React.ReactNode }[] = [
  { value: 'all', label: 'All Posts', labelAr: 'جميع المنشورات', icon: null },
  { value: 'published', label: 'Published', labelAr: 'منشور', icon: <CheckCircle color="success" fontSize="small" /> },
  { value: 'scheduled', label: 'Scheduled', labelAr: 'مجدول', icon: <Schedule color="info" fontSize="small" /> },
  { value: 'draft', label: 'Drafts', labelAr: 'مسودات', icon: <Drafts color="action" fontSize="small" /> },
  { value: 'failed', label: 'Failed', labelAr: 'فشل', icon: <Error color="error" fontSize="small" /> },
];

export const PostList: React.FC<PostListProps> = ({
  posts,
  loading = false,
  error = null,
  onEdit,
  onDelete,
  onPublish,
  onDuplicate,
  onBulkAction,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const language = useAppSelector(selectLanguage);
  
  // Filters and view state
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<PostStatus>('all');
  const [platformFilter, setPlatformFilter] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<'all' | 'today' | 'week' | 'month'>('all');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [selectedPosts, setSelectedPosts] = useState<number[]>([]);
  const [bulkActionMenu, setBulkActionMenu] = useState<null | HTMLElement>(null);
  
  // Pagination state
  const [page, setPage] = useState(1);
  const [itemsPerPage] = useState(12);

  // Filter posts based on criteria
  const filteredPosts = useMemo(() => {
    return posts.filter(post => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesCaption = post.caption?.toLowerCase().includes(query);
        const matchesCaptionAr = post.caption_ar?.toLowerCase().includes(query);
        const matchesHashtags = post.hashtags?.some(tag => tag.toLowerCase().includes(query));
        
        if (!matchesCaption && !matchesCaptionAr && !matchesHashtags) {
          return false;
        }
      }
      
      // Status filter
      if (statusFilter !== 'all' && post.status !== statusFilter) {
        return false;
      }
      
      // Platform filter
      if (platformFilter.length > 0) {
        const postPlatforms = post.platform || [];
        const hasMatchingPlatform = platformFilter.some(platform => 
          postPlatforms.includes(platform)
        );
        if (!hasMatchingPlatform) {
          return false;
        }
      }
      
      // Date range filter
      if (dateRange !== 'all' && post.created_at) {
        const postDate = new Date(post.created_at);
        const now = new Date();
        
        switch (dateRange) {
          case 'today':
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            if (postDate < today) return false;
            break;
          case 'week':
            const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            if (postDate < weekAgo) return false;
            break;
          case 'month':
            const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            if (postDate < monthAgo) return false;
            break;
        }
      }
      
      return true;
    });
  }, [posts, searchQuery, statusFilter, platformFilter, dateRange]);

  // Paginate filtered posts
  const paginatedPosts = useMemo(() => {
    const startIndex = (page - 1) * itemsPerPage;
    return filteredPosts.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredPosts, page, itemsPerPage]);

  const totalPages = Math.ceil(filteredPosts.length / itemsPerPage);

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
    setSelectedPosts([]);
  };

  const handleSelectAll = () => {
    if (selectedPosts.length === paginatedPosts.length) {
      setSelectedPosts([]);
    } else {
      setSelectedPosts(paginatedPosts.map(post => post.id));
    }
  };

  const handleSelectPost = (postId: number) => {
    setSelectedPosts(prev => 
      prev.includes(postId) 
        ? prev.filter(id => id !== postId)
        : [...prev, postId]
    );
  };

  const handleBulkAction = (action: string) => {
    if (onBulkAction && selectedPosts.length > 0) {
      onBulkAction(action, selectedPosts);
      setSelectedPosts([]);
    }
    setBulkActionMenu(null);
  };

  const getStatusCounts = () => {
    const counts: Record<PostStatus, number> = {
      all: posts.length,
      published: posts.filter(p => p.status === 'published').length,
      scheduled: posts.filter(p => p.status === 'scheduled').length,
      draft: posts.filter(p => p.status === 'draft').length,
      failed: posts.filter(p => p.status === 'failed').length,
    };
    return counts;
  };

  const statusCounts = getStatusCounts();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h5" gutterBottom>
          {language === 'ar' ? 'المنشورات' : 'Posts'}
        </Typography>
        
        {/* Status Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Stack direction="row" spacing={2} sx={{ overflowX: 'auto', pb: 1 }}>
            {statusOptions.map(option => (
              <Chip
                key={option.value}
                label={
                  <Box display="flex" alignItems="center" gap={0.5}>
                    {option.icon}
                    <span>
                      {language === 'ar' ? option.labelAr : option.label}
                    </span>
                    <Typography variant="caption" component="span" sx={{ ml: 0.5 }}>
                      ({statusCounts[option.value]})
                    </Typography>
                  </Box>
                }
                onClick={() => setStatusFilter(option.value)}
                color={statusFilter === option.value ? 'primary' : 'default'}
                variant={statusFilter === option.value ? 'filled' : 'outlined'}
              />
            ))}
          </Stack>
        </Box>
      </Box>

      {/* Filters and Actions */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          {/* Search */}
          <Grid xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder={language === 'ar' ? 'البحث في المنشورات...' : 'Search posts...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          
          {/* Platform Filter */}
          <Grid xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>
                {language === 'ar' ? 'المنصات' : 'Platforms'}
              </InputLabel>
              <Select
                multiple
                value={platformFilter}
                onChange={(e) => setPlatformFilter(e.target.value as string[])}
                renderValue={(selected) => (
                  <Box display="flex" flexWrap="wrap" gap={0.5}>
                    {selected.map(value => (
                      <Chip 
                        key={value} 
                        label={PLATFORM_LABELS[value as keyof typeof PLATFORM_LABELS]} 
                        size="small" 
                      />
                    ))}
                  </Box>
                )}
              >
                {Object.entries(PLATFORMS).map(([key, value]) => (
                  <MenuItem key={key} value={value}>
                    <Checkbox checked={platformFilter.includes(value)} />
                    <ListItemText primary={PLATFORM_LABELS[value]} />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Date Range */}
          <Grid xs={12} sm={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>
                {language === 'ar' ? 'الفترة' : 'Date Range'}
              </InputLabel>
              <Select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value as any)}
              >
                <MenuItem value="all">
                  {language === 'ar' ? 'الكل' : 'All Time'}
                </MenuItem>
                <MenuItem value="today">
                  {language === 'ar' ? 'اليوم' : 'Today'}
                </MenuItem>
                <MenuItem value="week">
                  {language === 'ar' ? 'هذا الأسبوع' : 'This Week'}
                </MenuItem>
                <MenuItem value="month">
                  {language === 'ar' ? 'هذا الشهر' : 'This Month'}
                </MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* View Mode Toggle */}
          <Grid xs={12} sm={6} md={1.5}>
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={(e, newMode) => newMode && setViewMode(newMode)}
              size="small"
              fullWidth
            >
              <ToggleButton value="grid">
                <ViewModule />
              </ToggleButton>
              <ToggleButton value="list">
                <ViewList />
              </ToggleButton>
            </ToggleButtonGroup>
          </Grid>
          
          {/* Bulk Actions */}
          <Grid xs={12} sm={6} md={1.5}>
            {selectedPosts.length > 0 && (
              <Button
                variant="outlined"
                size="small"
                fullWidth
                onClick={(e) => setBulkActionMenu(e.currentTarget)}
                endIcon={<MoreVert />}
              >
                {language === 'ar' 
                  ? `${selectedPosts.length} محدد`
                  : `${selectedPosts.length} selected`
                }
              </Button>
            )}
          </Grid>
        </Grid>
        
        {/* Select All */}
        {paginatedPosts.length > 0 && (
          <Box mt={2}>
            <Checkbox
              checked={selectedPosts.length === paginatedPosts.length}
              indeterminate={selectedPosts.length > 0 && selectedPosts.length < paginatedPosts.length}
              onChange={handleSelectAll}
            />
            <Typography variant="body2" component="span">
              {language === 'ar' ? 'تحديد الكل' : 'Select All'}
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Posts Grid/List */}
      {paginatedPosts.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            {language === 'ar' 
              ? 'لا توجد منشورات مطابقة للبحث'
              : 'No posts found matching your search'
            }
          </Typography>
        </Paper>
      ) : viewMode === 'grid' ? (
        <Grid container spacing={2}>
          {paginatedPosts.map(post => (
            <Grid xs={12} sm={6} md={4} key={post.id}>
              <PostCard
                post={post}
                onEdit={onEdit}
                onDelete={onDelete}
                onPublish={onPublish}
                onDuplicate={onDuplicate}
                selected={selectedPosts.includes(post.id)}
                onSelect={() => handleSelectPost(post.id)}
              />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Stack spacing={2}>
          {paginatedPosts.map(post => (
            <PostCard
              key={post.id}
              post={post}
              onEdit={onEdit}
              onDelete={onDelete}
              onPublish={onPublish}
              onDuplicate={onDuplicate}
              selected={selectedPosts.includes(post.id)}
              onSelect={() => handleSelectPost(post.id)}
              variant="list"
            />
          ))}
        </Stack>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={4}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={handlePageChange}
            color="primary"
            size={isMobile ? 'small' : 'medium'}
          />
        </Box>
      )}

      {/* Bulk Action Menu */}
      <Menu
        anchorEl={bulkActionMenu}
        open={Boolean(bulkActionMenu)}
        onClose={() => setBulkActionMenu(null)}
      >
        <MenuItem onClick={() => handleBulkAction('publish')}>
          {language === 'ar' ? 'نشر المحدد' : 'Publish Selected'}
        </MenuItem>
        <MenuItem onClick={() => handleBulkAction('schedule')}>
          {language === 'ar' ? 'جدولة المحدد' : 'Schedule Selected'}
        </MenuItem>
        <MenuItem onClick={() => handleBulkAction('draft')}>
          {language === 'ar' ? 'تحويل لمسودة' : 'Move to Draft'}
        </MenuItem>
        <MenuItem onClick={() => handleBulkAction('delete')} sx={{ color: 'error.main' }}>
          {language === 'ar' ? 'حذف المحدد' : 'Delete Selected'}
        </MenuItem>
      </Menu>
    </Box>
  );
};