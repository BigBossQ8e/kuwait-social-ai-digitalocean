import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Stack,
  Tooltip,
  Paper,
  Divider,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Language as LanguageIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { apiClient } from '../../../services/api/apiClient';

interface Translation {
  key: string;
  en: string;
  ar: string;
  category: string;
}

interface TranslationCategory {
  name: string;
  translations: Translation[];
}

const TranslationEditor: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [translations, setTranslations] = useState<TranslationCategory[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<{ en: string; ar: string }>({ en: '', ar: '' });
  const [loading, setLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showOnlyMissing, setShowOnlyMissing] = useState(false);

  useEffect(() => {
    loadTranslations();
  }, []);

  const loadTranslations = async () => {
    try {
      setLoading(true);
      // Fetch translations from backend API
      const response = await apiClient.get('/api/translations/list');
      setTranslations(response.data);
    } catch (err) {
      setError('Failed to load translations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const organizeTranslations = (en: any, ar: any): TranslationCategory[] => {
    const categories: { [key: string]: Translation[] } = {};
    
    const processObject = (obj: any, prefix = '', category = 'common') => {
      Object.keys(obj).forEach(key => {
        const fullKey = prefix ? `${prefix}.${key}` : key;
        
        if (typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
          // Determine category from top-level key
          const newCategory = prefix === '' ? key : category;
          processObject(obj[key], fullKey, newCategory);
        } else {
          if (!categories[category]) {
            categories[category] = [];
          }
          
          categories[category].push({
            key: fullKey,
            en: getNestedValue(en, fullKey) || '',
            ar: getNestedValue(ar, fullKey) || '',
            category
          });
        }
      });
    };
    
    processObject(en);
    
    return Object.entries(categories).map(([name, translations]) => ({
      name,
      translations
    }));
  };

  const getNestedValue = (obj: any, path: string): string => {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj) || '';
  };

  const setNestedValue = (obj: any, path: string, value: string): void => {
    const parts = path.split('.');
    const last = parts.pop()!;
    const target = parts.reduce((acc, part) => {
      if (!acc[part]) acc[part] = {};
      return acc[part];
    }, obj);
    target[last] = value;
  };

  const handleEdit = (translation: Translation) => {
    setEditingKey(translation.key);
    setEditValues({ en: translation.en, ar: translation.ar });
  };

  const handleSave = async (key: string) => {
    try {
      setSaveSuccess(false);
      setError(null);
      
      // Prepare updates for both locales
      const updates = [
        { key, locale: 'en', value: editValues.en },
        { key, locale: 'ar', value: editValues.ar }
      ];
      
      // Save to backend
      await apiClient.put('/api/translations/bulk', { updates });
      
      // Update local state
      const updatedTranslations = translations.map(category => ({
        ...category,
        translations: category.translations.map(t => 
          t.key === key ? { ...t, en: editValues.en, ar: editValues.ar } : t
        )
      }));
      setTranslations(updatedTranslations);
      
      // Update i18n resources for immediate UI update
      const enResources = i18n.getResourceBundle('en', 'translation');
      const arResources = i18n.getResourceBundle('ar', 'translation');
      
      setNestedValue(enResources, key, editValues.en);
      setNestedValue(arResources, key, editValues.ar);
      
      i18n.addResourceBundle('en', 'translation', enResources, true, true);
      i18n.addResourceBundle('ar', 'translation', arResources, true, true);
      
      setEditingKey(null);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError('Failed to save translation');
      console.error(err);
    }
  };

  const handleCancel = () => {
    setEditingKey(null);
    setEditValues({ en: '', ar: '' });
  };

  const exportTranslations = async () => {
    try {
      const response = await apiClient.get('/api/translations/export');
      const data = response.data;
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'translations.json';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export translations');
      console.error(err);
    }
  };

  const filteredTranslations = translations.map(category => ({
    ...category,
    translations: category.translations.filter(t => {
      const matchesSearch = searchTerm === '' || 
        t.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.en.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.ar.includes(searchTerm);
        
      const matchesCategory = selectedCategory === 'all' || category.name === selectedCategory;
      const matchesMissing = !showOnlyMissing || !t.ar || t.ar.trim() === '';
      
      return matchesSearch && matchesCategory && matchesMissing;
    })
  })).filter(category => category.translations.length > 0);

  const missingTranslationsCount = translations.reduce((acc, category) => 
    acc + category.translations.filter(t => !t.ar || t.ar.trim() === '').length, 0
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <LanguageIcon />
        Translation Manager
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search translations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Category"
              >
                <MenuItem value="all">All Categories</MenuItem>
                {translations.map(cat => (
                  <MenuItem key={cat.name} value={cat.name}>
                    {cat.name.charAt(0).toUpperCase() + cat.name.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControlLabel
              control={
                <Switch
                  checked={showOnlyMissing}
                  onChange={(e) => setShowOnlyMissing(e.target.checked)}
                />
              }
              label={`Missing Arabic (${missingTranslationsCount})`}
            />
          </Grid>
          
          <Grid item xs={12} md={2}>
            <Stack direction="row" spacing={1}>
              <Tooltip title="Refresh translations">
                <IconButton onClick={loadTranslations} disabled={loading}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={exportTranslations}
              >
                Export
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Translation saved successfully!
        </Alert>
      )}

      <Box>
        {filteredTranslations.map((category) => (
          <Accordion key={category.name} defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">
                {category.name.charAt(0).toUpperCase() + category.name.slice(1)}
              </Typography>
              <Chip 
                label={category.translations.length} 
                size="small" 
                sx={{ ml: 2 }}
              />
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {category.translations.map((translation) => (
                  <Grid item xs={12} key={translation.key}>
                    <Card variant="outlined">
                      <CardContent>
                        <Grid container spacing={2} alignItems="center">
                          <Grid item xs={12}>
                            <Typography variant="caption" color="text.secondary">
                              Key: {translation.key}
                            </Typography>
                          </Grid>
                          
                          <Grid item xs={12} md={5}>
                            {editingKey === translation.key ? (
                              <TextField
                                fullWidth
                                label="English"
                                value={editValues.en}
                                onChange={(e) => setEditValues({ ...editValues, en: e.target.value })}
                                multiline
                                rows={2}
                              />
                            ) : (
                              <Box>
                                <Typography variant="caption" color="text.secondary">
                                  English
                                </Typography>
                                <Typography>{translation.en}</Typography>
                              </Box>
                            )}
                          </Grid>
                          
                          <Grid item xs={12} md={5}>
                            {editingKey === translation.key ? (
                              <TextField
                                fullWidth
                                label="Arabic"
                                value={editValues.ar}
                                onChange={(e) => setEditValues({ ...editValues, ar: e.target.value })}
                                multiline
                                rows={2}
                                dir="rtl"
                              />
                            ) : (
                              <Box>
                                <Typography variant="caption" color="text.secondary">
                                  Arabic
                                </Typography>
                                <Typography dir="rtl">
                                  {translation.ar || (
                                    <Chip 
                                      label="Missing" 
                                      size="small" 
                                      color="warning" 
                                    />
                                  )}
                                </Typography>
                              </Box>
                            )}
                          </Grid>
                          
                          <Grid item xs={12} md={2}>
                            {editingKey === translation.key ? (
                              <Stack direction="row" spacing={1}>
                                <IconButton 
                                  color="primary" 
                                  onClick={() => handleSave(translation.key)}
                                >
                                  <CheckIcon />
                                </IconButton>
                                <IconButton 
                                  color="error" 
                                  onClick={handleCancel}
                                >
                                  <CloseIcon />
                                </IconButton>
                              </Stack>
                            ) : (
                              <IconButton 
                                onClick={() => handleEdit(translation)}
                                size="small"
                              >
                                <EditIcon />
                              </IconButton>
                            )}
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    </Box>
  );
};

export default TranslationEditor;