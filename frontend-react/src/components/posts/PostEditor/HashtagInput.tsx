// Hashtag input component with suggestions

import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Chip,
  TextField,
  Autocomplete,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  useTheme,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import { Tag, TrendingUp, Schedule, LocationOn } from '@mui/icons-material';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { fetchTrendingHashtags, getCurrentContext, type TrendingHashtag } from '../../../services/trendingHashtags';

interface HashtagInputProps {
  hashtags: string[];
  onAdd: (hashtag: string) => void;
  onRemove: (hashtag: string) => void;
  maxCount: number;
}

// Static hashtags for offline fallback
const fallbackHashtags = {
  kuwait: ['#Kuwait', '#الكويت', '#Q8', '#KuwaitCity', '#Kuwait2024'],
  business: ['#KuwaitBusiness', '#أعمال_الكويت', '#Entrepreneur', '#Startup', '#SmallBusiness'],
  food: ['#KuwaitFood', '#مطاعم_الكويت', '#Foodie', '#Restaurant', '#Cafe'],
  fashion: ['#KuwaitFashion', '#أزياء_الكويت', '#Style', '#Fashion', '#Shopping'],
  ramadan: ['#RamadanKuwait', '#رمضان_الكويت', '#Iftar', '#إفطار', '#رمضان'],
  national: ['#KuwaitNationalDay', '#العيد_الوطني_الكويتي', '#Feb25', '#Feb26', '#Liberation'],
};

export const HashtagInput: React.FC<HashtagInputProps> = ({
  hashtags,
  onAdd,
  onRemove,
  maxCount,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [trendingHashtags, setTrendingHashtags] = useState<TrendingHashtag[]>([]);
  const [loadingTrends, setLoadingTrends] = useState(false);
  const [currentContext, setCurrentContext] = useState<string>('');
  const inputRef = useRef<HTMLInputElement>(null);

  const fallbackSuggestions = Object.values(fallbackHashtags).flat();
  const remainingCount = maxCount - hashtags.length;

  // Fetch trending hashtags on mount and periodically
  useEffect(() => {
    const loadTrendingHashtags = async () => {
      setLoadingTrends(true);
      try {
        const trends = await fetchTrendingHashtags();
        setTrendingHashtags(trends);
        const context = getCurrentContext();
        setCurrentContext(context.context);
      } catch (error) {
        console.error('Failed to fetch trending hashtags:', error);
      } finally {
        setLoadingTrends(false);
      }
    };

    loadTrendingHashtags();
    // Refresh every 30 minutes
    const interval = setInterval(loadTrendingHashtags, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    let value = event.target.value;
    
    // Ensure hashtag starts with #
    if (value && !value.startsWith('#')) {
      value = '#' + value;
    }
    
    // Remove spaces from hashtag
    value = value.replace(/\s/g, '');
    
    setInputValue(value);
  };

  const handleAddHashtag = (tag: string) => {
    const cleanTag = tag.trim();
    
    if (cleanTag && 
        !hashtags.includes(cleanTag) && 
        hashtags.length < maxCount &&
        cleanTag.length > 1) {
      onAdd(cleanTag);
      setInputValue('');
      setShowSuggestions(false);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (inputValue.length > 1) {
        handleAddHashtag(inputValue);
      }
    }
  };

  const getSuggestions = () => {
    // Combine trending and static hashtags
    const allHashtags = [
      ...trendingHashtags.map(t => t.tag),
      ...trendingHashtags.map(t => t.tagAr).filter(tag => tag),
      ...fallbackSuggestions
    ];
    
    // Remove duplicates
    const uniqueHashtags = Array.from(new Set(allHashtags));
    
    if (!inputValue || inputValue === '#') {
      return uniqueHashtags.slice(0, 20);
    }
    
    const searchTerm = inputValue.toLowerCase();
    return uniqueHashtags
      .filter(tag => 
        tag.toLowerCase().includes(searchTerm) && !hashtags.includes(tag)
      )
      .slice(0, 15);
  };

  const suggestions = getSuggestions();
  
  const getTrendingInfo = (hashtag: string): TrendingHashtag | undefined => {
    return trendingHashtags.find(t => t.tag === hashtag || t.tagAr === hashtag);
  };

  return (
    <Box>
      {/* Current hashtags */}
      {hashtags.length > 0 && (
        <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
          {hashtags.map((tag) => (
            <Chip
              key={tag}
              label={tag}
              onDelete={() => onRemove(tag)}
              icon={<Tag fontSize="small" />}
              color="primary"
              variant="outlined"
            />
          ))}
        </Box>
      )}

      {/* Input field */}
      <Box position="relative">
        <TextField
          ref={inputRef}
          fullWidth
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder={
            language === 'ar' 
              ? remainingCount > 0 ? `أضف وسم... (${remainingCount} متبقي)` : 'تم الوصول للحد الأقصى'
              : remainingCount > 0 ? `Add hashtag... (${remainingCount} remaining)` : 'Maximum reached'
          }
          disabled={hashtags.length >= maxCount}
          size="small"
          InputProps={{
            startAdornment: <Tag fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />,
          }}
        />

        {/* Suggestions dropdown */}
        {showSuggestions && suggestions.length > 0 && remainingCount > 0 && (
          <Paper
            sx={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              mt: 0.5,
              maxHeight: 300,
              overflow: 'auto',
              zIndex: 1000,
              boxShadow: theme.shadows[4],
            }}
          >
            <List dense>
              {inputValue.length > 1 && !suggestions.includes(inputValue) && (
                <ListItemButton onClick={() => handleAddHashtag(inputValue)}>
                  <ListItemText 
                    primary={
                      <Box display="flex" alignItems="center">
                        <Tag fontSize="small" sx={{ mr: 1 }} />
                        <Typography variant="body2">
                          {language === 'ar' ? 'استخدم: ' : 'Use: '}
                          <strong>{inputValue}</strong>
                        </Typography>
                      </Box>
                    }
                  />
                </ListItemButton>
              )}
              
              {suggestions.slice(0, 10).map((tag) => (
                <ListItemButton 
                  key={tag} 
                  onClick={() => handleAddHashtag(tag)}
                  sx={{
                    '&:hover': {
                      backgroundColor: theme.palette.action.hover,
                    },
                  }}
                >
                  <ListItemText 
                    primary={
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box display="flex" alignItems="center">
                          <Tag fontSize="small" sx={{ mr: 1 }} />
                          <Typography variant="body2">{tag}</Typography>
                        </Box>
                        {getTrendingInfo(tag) && (
                          <Tooltip title={getTrendingInfo(tag)?.description || `Trending ${getTrendingInfo(tag)?.category}`}>
                            <Box display="flex" alignItems="center" gap={0.5}>
                              {getTrendingInfo(tag)?.category === 'location' && (
                                <LocationOn fontSize="small" color="info" />
                              )}
                              {['morning', 'afternoon', 'evening', 'night'].includes(getTrendingInfo(tag)?.category || '') && (
                                <Schedule fontSize="small" color="secondary" />
                              )}
                              <TrendingUp fontSize="small" color="primary" />
                              <Typography variant="caption" color="primary">
                                {getTrendingInfo(tag)?.relevance}%
                              </Typography>
                            </Box>
                          </Tooltip>
                        )}
                      </Box>
                    }
                  />
                </ListItemButton>
              ))}
            </List>
          </Paper>
        )}
      </Box>

      {/* Popular hashtags */}
      {hashtags.length === 0 && (
        <Box mt={2}>
          {currentContext && (
            <Typography variant="caption" color="primary" gutterBottom display="block">
              <Schedule fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
              {currentContext}
            </Typography>
          )}
          <Typography variant="caption" color="text.secondary" gutterBottom>
            {language === 'ar' ? 'الوسوم الشائعة الآن:' : 'Trending now:'}
            {loadingTrends && <CircularProgress size={12} sx={{ ml: 1 }} />}
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={0.5} mt={1}>
            {suggestions.slice(0, 12).map((tag) => {
              const trendInfo = getTrendingInfo(tag);
              return (
                <Tooltip key={tag} title={trendInfo?.description || ''}>
                  <Chip
                    label={tag}
                    size="small"
                    variant={trendInfo ? "filled" : "outlined"}
                    color={trendInfo && trendInfo.relevance > 90 ? "primary" : "default"}
                    onClick={() => handleAddHashtag(tag)}
                    icon={
                      trendInfo?.category === 'location' ? <LocationOn fontSize="small" /> :
                      ['morning', 'afternoon', 'evening', 'night'].includes(trendInfo?.category || '') ? <Schedule fontSize="small" /> :
                      trendInfo ? <TrendingUp fontSize="small" /> : undefined
                    }
                    sx={{
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: theme.palette.action.hover,
                      },
                    }}
                  />
                </Tooltip>
              );
            })}
          </Box>
        </Box>
      )}

      {/* Hashtag counter */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
        <Typography variant="caption" color="text.secondary">
          {language === 'ar' 
            ? `${hashtags.length} / ${maxCount} وسم`
            : `${hashtags.length} / ${maxCount} hashtags`
          }
        </Typography>
        
        {hashtags.length > 15 && (
          <Typography variant="caption" color="warning.main">
            {language === 'ar' 
              ? 'تجنب استخدام الكثير من الوسوم'
              : 'Avoid using too many hashtags'
            }
          </Typography>
        )}
      </Box>
    </Box>
  );
};