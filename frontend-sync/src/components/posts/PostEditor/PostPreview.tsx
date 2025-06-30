// Post preview modal component

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Chip,
  Avatar,
  Card,
  CardHeader,
  CardContent,
  CardMedia,
  IconButton,
  Tabs,
  Tab,
  Paper,
  useTheme,
} from '@mui/material';
import {
  Close,
  FavoriteBorder,
  ChatBubbleOutline,
  Send,
  BookmarkBorder,
  Instagram,
  Twitter,
  CameraAlt,
} from '@mui/icons-material';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { PLATFORMS, PLATFORM_LABELS } from '../../../utils/constants';
import type { PostDraft } from '../../../types/api.types';

interface PostPreviewProps {
  post: PostDraft;
  open: boolean;
  onClose: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`platform-tabpanel-${index}`}
      aria-labelledby={`platform-tab-${index}`}
      {...other}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

export const PostPreview: React.FC<PostPreviewProps> = ({
  post,
  open,
  onClose,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const [selectedPlatform, setSelectedPlatform] = React.useState(0);

  const handlePlatformChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedPlatform(newValue);
  };

  const renderInstagramPreview = () => (
    <Card sx={{ maxWidth: 400, mx: 'auto' }}>
      <CardHeader
        avatar={
          <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
            K
          </Avatar>
        }
        action={
          <IconButton>
            <Close />
          </IconButton>
        }
        title="Kuwait Business"
        subheader="Just now"
      />
      
      {post.media_files && post.media_files.length > 0 && (
        <CardMedia
          component="img"
          height="400"
          image={post.media_files[0].url}
          alt="Post media"
          sx={{ objectFit: 'cover' }}
        />
      )}
      
      <Box sx={{ px: 2, py: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box display="flex" gap={1}>
            <IconButton>
              <FavoriteBorder />
            </IconButton>
            <IconButton>
              <ChatBubbleOutline />
            </IconButton>
            <IconButton>
              <Send />
            </IconButton>
          </Box>
          <IconButton>
            <BookmarkBorder />
          </IconButton>
        </Box>
      </Box>
      
      <CardContent sx={{ pt: 0 }}>
        <Typography variant="body2" gutterBottom style={{ whiteSpace: 'pre-wrap' }}>
          {post.caption}
        </Typography>
        
        {post.hashtags.length > 0 && (
          <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
            {post.hashtags.join(' ')}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  const renderTwitterPreview = () => (
    <Card sx={{ maxWidth: 500, mx: 'auto' }}>
      <CardContent>
        <Box display="flex" alignItems="flex-start" gap={2}>
          <Avatar sx={{ bgcolor: theme.palette.primary.main }}>K</Avatar>
          <Box flex={1}>
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="subtitle2" fontWeight="bold">
                Kuwait Business
              </Typography>
              <Typography variant="caption" color="text.secondary">
                @kuwaitbusiness · now
              </Typography>
            </Box>
            
            <Typography variant="body2" sx={{ mt: 1 }} style={{ whiteSpace: 'pre-wrap' }}>
              {post.caption}
            </Typography>
            
            {post.hashtags.length > 0 && (
              <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                {post.hashtags.join(' ')}
              </Typography>
            )}
            
            {post.media_files && post.media_files.length > 0 && (
              <Box
                component="img"
                src={post.media_files[0].url}
                alt="Tweet media"
                sx={{
                  width: '100%',
                  mt: 2,
                  borderRadius: 2,
                  maxHeight: 300,
                  objectFit: 'cover',
                }}
              />
            )}
            
            <Box display="flex" justifyContent="space-between" mt={2}>
              <IconButton size="small">
                <ChatBubbleOutline fontSize="small" />
              </IconButton>
              <IconButton size="small">
                <Send fontSize="small" sx={{ transform: 'rotate(-45deg)' }} />
              </IconButton>
              <IconButton size="small">
                <FavoriteBorder fontSize="small" />
              </IconButton>
              <IconButton size="small">
                <BookmarkBorder fontSize="small" />
              </IconButton>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const renderSnapchatPreview = () => (
    <Card sx={{ maxWidth: 360, mx: 'auto', backgroundColor: '#FFFC00', color: '#000' }}>
      <CardContent sx={{ textAlign: 'center', py: 4 }}>
        <CameraAlt sx={{ fontSize: 48, mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Snapchat Preview
        </Typography>
        
        {post.media_files && post.media_files.length > 0 && (
          <Box
            component="img"
            src={post.media_files[0].url}
            alt="Snap media"
            sx={{
              width: '100%',
              borderRadius: 2,
              mb: 2,
              maxHeight: 400,
              objectFit: 'cover',
            }}
          />
        )}
        
        <Typography variant="body1" sx={{ mb: 2 }} style={{ whiteSpace: 'pre-wrap' }}>
          {post.caption}
        </Typography>
        
        {post.hashtags.length > 0 && (
          <Typography variant="body2">
            {post.hashtags.join(' ')}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  const platforms = post.platform || ['instagram'];

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { minHeight: 600 }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            {language === 'ar' ? 'معاينة المنشور' : 'Post Preview'}
          </Typography>
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {platforms.length > 1 && (
          <Tabs
            value={selectedPlatform}
            onChange={handlePlatformChange}
            centered
            sx={{ mb: 3 }}
          >
            {platforms.map((platform, index) => (
              <Tab
                key={platform}
                label={PLATFORM_LABELS[platform as keyof typeof PLATFORM_LABELS]}
                icon={
                  platform === 'instagram' ? <Instagram /> :
                  platform === 'twitter' ? <Twitter /> :
                  <CameraAlt />
                }
                iconPosition="start"
              />
            ))}
          </Tabs>
        )}
        
        {platforms.map((platform, index) => (
          <TabPanel key={platform} value={selectedPlatform} index={index}>
            {platform === 'instagram' && renderInstagramPreview()}
            {platform === 'twitter' && renderTwitterPreview()}
            {platform === 'snapchat' && renderSnapchatPreview()}
          </TabPanel>
        ))}
        
        {post.caption_ar && (
          <Box mt={3}>
            <Typography variant="subtitle2" gutterBottom color="text.secondary">
              {language === 'ar' ? 'النسخة العربية:' : 'Arabic Version:'}
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, direction: 'rtl' }}>
              <Typography variant="body2" style={{ whiteSpace: 'pre-wrap' }}>
                {post.caption_ar}
              </Typography>
            </Paper>
          </Box>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          {language === 'ar' ? 'إغلاق' : 'Close'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};