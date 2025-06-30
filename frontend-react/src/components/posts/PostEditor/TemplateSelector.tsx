// Template Selector Component with AI Integration
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  AutoAwesome as AIIcon,
  ExpandMore as ExpandMoreIcon,
  Close as CloseIcon,
  Psychology as PromptIcon,
  Category as CategoryIcon,
  Tag as TagIcon,
} from '@mui/icons-material';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { contentTemplates, getTemplateCategories, type ContentTemplate } from '../../../data/contentTemplates';
import { api } from '../../../services/api';

interface TemplateSelectorProps {
  onContentGenerated: (content: {
    content_en: string;
    content_ar?: string;
    hashtags: string[];
  }) => void;
  businessType?: string;
  platform?: string;
}

export const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  onContentGenerated,
  businessType = 'restaurant',
  platform = 'instagram',
}) => {
  const language = useAppSelector(selectLanguage);
  const [open, setOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<ContentTemplate | null>(null);
  const [templateValues, setTemplateValues] = useState<Record<string, string>>({});
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>('all');

  const categories = ['all', ...getTemplateCategories()];
  
  const filteredTemplates = activeCategory === 'all' 
    ? contentTemplates 
    : contentTemplates.filter(t => t.category === activeCategory);

  const handleTemplateSelect = (template: ContentTemplate) => {
    setSelectedTemplate(template);
    // Initialize template values with examples
    const initialValues: Record<string, string> = {};
    Object.entries(template.placeholders).forEach(([key, placeholder]) => {
      initialValues[key] = placeholder.example;
    });
    setTemplateValues(initialValues);
  };

  const handleValueChange = (key: string, value: string) => {
    setTemplateValues(prev => ({ ...prev, [key]: value }));
  };

  const buildPrompt = (): string => {
    if (!selectedTemplate) return '';
    
    let prompt = language === 'ar' ? selectedTemplate.promptAr : selectedTemplate.prompt;
    
    // Replace placeholders with actual values
    Object.entries(templateValues).forEach(([key, value]) => {
      prompt = prompt.replace(new RegExp(`{${key}}`, 'g'), value);
    });
    
    return prompt;
  };

  const handleGenerateContent = async () => {
    if (!selectedTemplate) return;
    
    setGenerating(true);
    setError(null);
    
    try {
      const prompt = buildPrompt();
      const response = await api.post('/content/generate', {
        prompt,
        platform,
        tone: 'professional',
        include_arabic: true,
        include_hashtags: true,
        business_context: {
          type: businessType,
          location: 'Kuwait',
          template_id: selectedTemplate.id
        }
      });
      
      if (response.content_en) {
        onContentGenerated({
          content_en: response.content_en,
          content_ar: response.content_ar,
          hashtags: [...(response.hashtags || []), ...selectedTemplate.hashtags]
        });
        setOpen(false);
        setSelectedTemplate(null);
      } else {
        throw new Error('No content generated');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate content. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <>
      <Button
        variant="outlined"
        startIcon={<AIIcon />}
        onClick={() => setOpen(true)}
        fullWidth
        sx={{ mb: 2 }}
      >
        {language === 'ar' ? 'استخدم قالب مع الذكاء الاصطناعي' : 'Use AI Template'}
      </Button>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {language === 'ar' ? 'قوالب المحتوى' : 'Content Templates'}
            </Typography>
            <IconButton onClick={() => setOpen(false)} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent dividers>
          {/* Category Filter */}
          <Box mb={3}>
            <Typography variant="subtitle2" gutterBottom>
              <CategoryIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
              {language === 'ar' ? 'الفئات' : 'Categories'}
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {categories.map(cat => (
                <Chip
                  key={cat}
                  label={cat.charAt(0).toUpperCase() + cat.slice(1)}
                  onClick={() => setActiveCategory(cat)}
                  color={activeCategory === cat ? 'primary' : 'default'}
                  variant={activeCategory === cat ? 'filled' : 'outlined'}
                />
              ))}
            </Box>
          </Box>

          {/* Template List */}
          {!selectedTemplate ? (
            <Grid container spacing={2}>
              {filteredTemplates.map(template => (
                <Grid item xs={12} sm={6} key={template.id}>
                  <Card 
                    variant="outlined"
                    sx={{
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': {
                        boxShadow: 2,
                        borderColor: 'primary.main',
                      }
                    }}
                    onClick={() => handleTemplateSelect(template)}
                  >
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {language === 'ar' ? template.titleAr : template.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {language === 'ar' ? template.promptAr : template.prompt}
                      </Typography>
                      <Box display="flex" gap={0.5} flexWrap="wrap">
                        {template.hashtags.slice(0, 3).map(tag => (
                          <Chip key={tag} label={tag} size="small" />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            /* Template Customization */
            <Box>
              <Typography variant="h6" gutterBottom>
                {language === 'ar' ? selectedTemplate.titleAr : selectedTemplate.title}
              </Typography>
              
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {/* Placeholder Inputs */}
              <Box sx={{ mb: 3 }}>
                {Object.entries(selectedTemplate.placeholders).map(([key, placeholder]) => (
                  <Box key={key} sx={{ mb: 2 }}>
                    <TextField
                      fullWidth
                      label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      value={templateValues[key] || ''}
                      onChange={(e) => handleValueChange(key, e.target.value)}
                      helperText={language === 'ar' ? placeholder.exampleAr : placeholder.example}
                      multiline={key.includes('description') || key.includes('features')}
                      rows={2}
                    />
                    {placeholder.suggestions && (
                      <Box display="flex" gap={0.5} flexWrap="wrap" mt={1}>
                        {placeholder.suggestions.slice(0, 4).map(suggestion => (
                          <Chip
                            key={suggestion}
                            label={suggestion}
                            size="small"
                            variant="outlined"
                            onClick={() => handleValueChange(key, suggestion)}
                            sx={{ cursor: 'pointer' }}
                          />
                        ))}
                      </Box>
                    )}
                  </Box>
                ))}
              </Box>

              {/* Preview */}
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>
                    <PromptIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
                    {language === 'ar' ? 'معاينة النص' : 'Prompt Preview'}
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {buildPrompt()}
                  </Typography>
                </AccordionDetails>
              </Accordion>

              {/* Suggested Hashtags */}
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  <TagIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
                  {language === 'ar' ? 'الوسوم المقترحة' : 'Suggested Hashtags'}
                </Typography>
                <Box display="flex" gap={0.5} flexWrap="wrap">
                  {selectedTemplate.hashtags.map(tag => (
                    <Chip key={tag} label={tag} size="small" color="primary" variant="outlined" />
                  ))}
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          {selectedTemplate && (
            <>
              <Button onClick={() => setSelectedTemplate(null)}>
                {language === 'ar' ? 'رجوع' : 'Back'}
              </Button>
              <Button
                variant="contained"
                onClick={handleGenerateContent}
                disabled={generating}
                startIcon={generating ? <CircularProgress size={16} /> : <AIIcon />}
              >
                {generating 
                  ? (language === 'ar' ? 'جاري الإنشاء...' : 'Generating...') 
                  : (language === 'ar' ? 'إنشاء المحتوى' : 'Generate Content')
                }
              </Button>
            </>
          )}
        </DialogActions>

        {generating && <LinearProgress />}
      </Dialog>
    </>
  );
};