// Post editor component with rich text editing

import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Chip,
  Alert,
  IconButton,
  Divider,
  ToggleButton,
  ToggleButtonGroup,
  Stack,
  Tooltip,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Save,
  Schedule,
  Send,
  AddAPhoto,
  Close,
  AutoAwesome,
  Translate,
  Tag,
  Preview,
} from '@mui/icons-material';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Link from '@tiptap/extension-link';
import Mention from '@tiptap/extension-mention';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { PLATFORMS, PLATFORM_LABELS, VALIDATION } from '../../../utils/constants';
import { MediaUpload } from './MediaUpload';
import { HashtagInput } from './HashtagInput';
import { PostPreview } from './PostPreview';
import type { PostDraft } from '../../../types/api.types';

interface PostEditorProps {
  initialData?: Partial<PostDraft>;
  onSave?: (post: PostDraft, action: 'save' | 'schedule' | 'publish') => void;
  onCancel?: () => void;
  mode?: 'create' | 'edit';
}

export const PostEditor: React.FC<PostEditorProps> = ({
  initialData,
  onSave,
  onCancel,
  mode = 'create',
}) => {
  const language = useAppSelector(selectLanguage);
  
  // Form state
  const [caption, setCaption] = useState(initialData?.caption || '');
  const [captionAr, setCaptionAr] = useState(initialData?.caption_ar || '');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(
    initialData?.platform || ['instagram']
  );
  const [hashtags, setHashtags] = useState<string[]>(initialData?.hashtags || []);
  const [mediaFiles, setMediaFiles] = useState<any[]>(initialData?.media_files || []);
  const [scheduledTime, setScheduledTime] = useState(initialData?.scheduled_time || '');
  const [showPreview, setShowPreview] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Rich text editor for English caption
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: language === 'ar' 
          ? 'اكتب محتوى منشورك هنا...' 
          : 'Write your post content here...',
      }),
      Link.configure({
        openOnClick: false,
      }),
      Mention.configure({
        HTMLAttributes: {
          class: 'mention',
        },
      }),
    ],
    content: caption,
    onUpdate: ({ editor }) => {
      setCaption(editor.getText());
    },
  });

  // Rich text editor for Arabic caption
  const editorAr = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: 'اكتب محتوى منشورك بالعربية هنا...',
      }),
      Link.configure({
        openOnClick: false,
      }),
      Mention.configure({
        HTMLAttributes: {
          class: 'mention',
        },
      }),
    ],
    content: captionAr,
    onUpdate: ({ editor }) => {
      setCaptionAr(editor.getText());
    },
  });

  const handlePlatformChange = (
    event: React.MouseEvent<HTMLElement>,
    newPlatforms: string[]
  ) => {
    setSelectedPlatforms(newPlatforms.length > 0 ? newPlatforms : ['instagram']);
  };

  const handleAddHashtag = (tag: string) => {
    if (hashtags.length < VALIDATION.HASHTAG_MAX_COUNT) {
      setHashtags([...hashtags, tag]);
    }
  };

  const handleRemoveHashtag = (tagToRemove: string) => {
    setHashtags(hashtags.filter(tag => tag !== tagToRemove));
  };

  const handleMediaUpload = (files: File[]) => {
    // Process uploaded files
    const newMediaFiles = files.map(file => ({
      id: Date.now() + Math.random(),
      file,
      url: URL.createObjectURL(file),
      type: file.type.startsWith('image/') ? 'image' : 'video',
    }));
    setMediaFiles([...mediaFiles, ...newMediaFiles]);
  };

  const handleRemoveMedia = (mediaId: string | number) => {
    setMediaFiles(mediaFiles.filter(media => media.id !== mediaId));
  };

  const handleGenerateContent = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      // Mock AI content generation - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const generatedContent = language === 'ar' 
        ? 'محتوى تم إنشاؤه بواسطة الذكاء الاصطناعي للأعمال في الكويت 🚀'
        : 'AI-generated content for Kuwait businesses 🚀';
      
      if (editor) {
        editor.commands.setContent(generatedContent);
      }
      setCaption(generatedContent);
    } catch (err) {
      setError(language === 'ar' 
        ? 'فشل في توليد المحتوى' 
        : 'Failed to generate content'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleTranslate = async () => {
    if (!caption) return;
    
    setIsGenerating(true);
    try {
      // Mock translation - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const translatedContent = 'ترجمة: ' + caption;
      if (editorAr) {
        editorAr.commands.setContent(translatedContent);
      }
      setCaptionAr(translatedContent);
    } catch (err) {
      setError(language === 'ar' 
        ? 'فشل في الترجمة' 
        : 'Translation failed'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const validatePost = (): boolean => {
    if (!caption.trim()) {
      setError(language === 'ar' 
        ? 'يرجى إدخال محتوى المنشور' 
        : 'Please enter post content'
      );
      return false;
    }
    
    if (caption.length > VALIDATION.POST_CAPTION_MAX_LENGTH) {
      setError(language === 'ar' 
        ? `تجاوز الحد الأقصى للأحرف (${VALIDATION.POST_CAPTION_MAX_LENGTH})` 
        : `Caption exceeds maximum length (${VALIDATION.POST_CAPTION_MAX_LENGTH})`
      );
      return false;
    }
    
    if (selectedPlatforms.length === 0) {
      setError(language === 'ar' 
        ? 'يرجى اختيار منصة واحدة على الأقل' 
        : 'Please select at least one platform'
      );
      return false;
    }
    
    return true;
  };

  const handleAction = (action: 'save' | 'schedule' | 'publish') => {
    if (!validatePost()) return;
    
    const postData: PostDraft = {
      caption,
      caption_ar: captionAr,
      hashtags,
      platform: selectedPlatforms,
      scheduled_time: action === 'schedule' ? scheduledTime : undefined,
      media_files: mediaFiles,
    };
    
    onSave?.(postData, action);
  };

  const characterCount = caption.length;
  const characterLimit = VALIDATION.POST_CAPTION_MAX_LENGTH;
  const characterPercentage = (characterCount / characterLimit) * 100;

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid xs={12} lg={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {mode === 'create' 
                ? (language === 'ar' ? 'إنشاء منشور جديد' : 'Create New Post')
                : (language === 'ar' ? 'تعديل المنشور' : 'Edit Post')
              }
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            {error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}
            
            {/* Platform Selection */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                {language === 'ar' ? 'اختر المنصات' : 'Select Platforms'}
              </Typography>
              <ToggleButtonGroup
                value={selectedPlatforms}
                onChange={handlePlatformChange}
                aria-label="platform selection"
                size="small"
              >
                {Object.entries(PLATFORMS).map(([key, value]) => (
                  <ToggleButton key={key} value={value}>
                    {PLATFORM_LABELS[value]}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Box>
            
            {/* Caption Editor */}
            <Box mb={3}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle2">
                  {language === 'ar' ? 'المحتوى' : 'Content'}
                </Typography>
                <Box display="flex" gap={1}>
                  <Tooltip title={language === 'ar' ? 'توليد بالذكاء الاصطناعي' : 'AI Generate'}>
                    <IconButton 
                      size="small" 
                      onClick={handleGenerateContent}
                      disabled={isGenerating}
                    >
                      <AutoAwesome />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title={language === 'ar' ? 'ترجمة' : 'Translate'}>
                    <IconButton 
                      size="small" 
                      onClick={handleTranslate}
                      disabled={!caption || isGenerating}
                    >
                      <Translate />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 2, 
                  minHeight: 200,
                  '& .ProseMirror': {
                    minHeight: 180,
                    outline: 'none',
                  },
                  '& .mention': {
                    color: 'primary.main',
                    fontWeight: 500,
                  }
                }}
              >
                <EditorContent editor={editor} />
              </Paper>
              
              <Box display="flex" justifyContent="space-between" mt={1}>
                <Typography variant="caption" color="text.secondary">
                  {language === 'ar' 
                    ? `${characterCount} / ${characterLimit} حرف`
                    : `${characterCount} / ${characterLimit} characters`
                  }
                </Typography>
                <Box 
                  sx={{ 
                    width: 100, 
                    height: 4, 
                    backgroundColor: 'grey.300',
                    borderRadius: 2,
                    overflow: 'hidden',
                  }}
                >
                  <Box 
                    sx={{ 
                      width: `${Math.min(characterPercentage, 100)}%`,
                      height: '100%',
                      backgroundColor: characterPercentage > 90 ? 'error.main' : 'primary.main',
                      transition: 'width 0.3s ease',
                    }}
                  />
                </Box>
              </Box>
            </Box>
            
            {/* Arabic Caption (Optional) */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                {language === 'ar' ? 'المحتوى بالعربية (اختياري)' : 'Arabic Content (Optional)'}
              </Typography>
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 2,
                  minHeight: 150,
                  direction: 'rtl',
                  '& .ProseMirror': {
                    minHeight: 130,
                    outline: 'none',
                    textAlign: 'right',
                  }
                }}
              >
                <EditorContent editor={editorAr} />
              </Paper>
            </Box>
            
            {/* Media Upload */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                {language === 'ar' ? 'الوسائط' : 'Media'}
              </Typography>
              <MediaUpload 
                files={mediaFiles}
                onUpload={handleMediaUpload}
                onRemove={handleRemoveMedia}
                maxFiles={selectedPlatforms.includes('instagram') ? 10 : 4}
              />
            </Box>
            
            {/* Hashtags */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                {language === 'ar' ? 'الوسوم' : 'Hashtags'}
              </Typography>
              <HashtagInput 
                hashtags={hashtags}
                onAdd={handleAddHashtag}
                onRemove={handleRemoveHashtag}
                maxCount={VALIDATION.HASHTAG_MAX_COUNT}
              />
            </Box>
            
            {/* Schedule Time (for scheduling) */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                {language === 'ar' ? 'جدولة النشر (اختياري)' : 'Schedule Post (Optional)'}
              </Typography>
              <TextField
                type="datetime-local"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                fullWidth
                InputLabelProps={{ shrink: true }}
                inputProps={{
                  min: new Date().toISOString().slice(0, 16),
                }}
              />
            </Box>
            
            {/* Action Buttons */}
            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button onClick={onCancel}>
                {language === 'ar' ? 'إلغاء' : 'Cancel'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<Preview />}
                onClick={() => setShowPreview(true)}
              >
                {language === 'ar' ? 'معاينة' : 'Preview'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<Save />}
                onClick={() => handleAction('save')}
              >
                {language === 'ar' ? 'حفظ كمسودة' : 'Save as Draft'}
              </Button>
              {scheduledTime && (
                <Button
                  variant="contained"
                  startIcon={<Schedule />}
                  onClick={() => handleAction('schedule')}
                >
                  {language === 'ar' ? 'جدولة' : 'Schedule'}
                </Button>
              )}
              <Button
                variant="contained"
                startIcon={<Send />}
                onClick={() => handleAction('publish')}
              >
                {language === 'ar' ? 'نشر الآن' : 'Publish Now'}
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        {/* Sidebar with tips */}
        <Grid xs={12} lg={4}>
          <Paper sx={{ p: 3, position: 'sticky', top: 24 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'ar' ? 'نصائح للنشر' : 'Posting Tips'}
            </Typography>
            <Stack spacing={2}>
              <Alert severity="info">
                <Typography variant="body2">
                  {language === 'ar' 
                    ? '🕐 أفضل أوقات النشر في الكويت: 6-8 مساءً و 9-11 مساءً'
                    : '🕐 Best posting times in Kuwait: 6-8 PM and 9-11 PM'
                  }
                </Typography>
              </Alert>
              
              <Alert severity="success">
                <Typography variant="body2">
                  {language === 'ar'
                    ? '# استخدم الهاشتاقات المحلية مثل #الكويت #Q8'
                    : '# Use local hashtags like #Kuwait #Q8'
                  }
                </Typography>
              </Alert>
              
              <Alert severity="warning">
                <Typography variant="body2">
                  {language === 'ar'
                    ? '📸 الصور عالية الجودة تحصل على تفاعل أكثر بنسبة 38%'
                    : '📸 High-quality images get 38% more engagement'
                  }
                </Typography>
              </Alert>
              
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  {language === 'ar' ? 'اختصارات لوحة المفاتيح' : 'Keyboard Shortcuts'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Ctrl/Cmd + B - {language === 'ar' ? 'خط عريض' : 'Bold'}<br />
                  • Ctrl/Cmd + I - {language === 'ar' ? 'خط مائل' : 'Italic'}<br />
                  • Ctrl/Cmd + K - {language === 'ar' ? 'إدراج رابط' : 'Insert link'}<br />
                  • @ - {language === 'ar' ? 'إشارة لشخص' : 'Mention someone'}
                </Typography>
              </Box>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Preview Modal */}
      {showPreview && (
        <PostPreview
          post={{
            caption,
            caption_ar: captionAr,
            hashtags,
            platform: selectedPlatforms,
            media_files: mediaFiles,
          }}
          open={showPreview}
          onClose={() => setShowPreview(false)}
        />
      )}
    </Box>
  );
};