import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Paper,
  Divider,
  Tooltip,
  Fab,
} from '@mui/material';
import {
  AutoAwesome,
  Refresh,
  Download,
  Upload,
  Schedule,
  ContentCopy,
  TrendingUp,
  Tag,
  AccessTime,
  Check,
} from '@mui/icons-material';
import defaultConfigJson from '../../config/postCreatorConfig.json';

interface ConfigData {
  promptsData: any;
  hashtagConfig: any;
  schedulingConfig: any;
  trendingConfig: any;
  aiConfig: any;
}

interface FormData {
  [key: string]: string | number;
}

export const PostCreator: React.FC = () => {
  // State management
  const [config, setConfig] = useState<ConfigData>(defaultConfigJson);
  const [selectedGoal, setSelectedGoal] = useState<string>('');
  const [selectedPrompt, setSelectedPrompt] = useState<string>('');
  const [formData, setFormData] = useState<FormData>({});
  const [generatedContent, setGeneratedContent] = useState<string>('');
  const [generatedHashtags, setGeneratedHashtags] = useState<string[]>([]);
  const [trendingHashtags, setTrendingHashtags] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingTrends, setIsLoadingTrends] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [copied, setCopied] = useState(false);

  // Fetch trending hashtags on component mount and when refreshed
  useEffect(() => {
    fetchTrendingHashtags();
  }, []);

  // Helper function to check if it's Ramadan
  const isRamadan = (): boolean => {
    const today = new Date();
    const year = today.getFullYear();
    // Simplified Ramadan check - in production, use proper Islamic calendar
    const ramadanStart = new Date(year, 2, 11); // Approximate
    const ramadanEnd = new Date(year, 3, 10); // Approximate
    return today >= ramadanStart && today <= ramadanEnd;
  };

  // Simulate fetching trending hashtags based on time of day
  const fetchTrendingHashtags = async () => {
    setIsLoadingTrends(true);
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const hour = new Date().getHours();
      const day = new Date().getDay();
      let trends: string[] = [];
      
      // Time-based trends
      if (hour >= 6 && hour < 11) {
        trends = [...config.trendingConfig.morning];
      } else if (hour >= 11 && hour < 16) {
        trends = [...config.trendingConfig.afternoon];
      } else if (hour >= 16 && hour < 22) {
        trends = [...config.trendingConfig.evening];
      } else {
        trends = [...config.trendingConfig.lateNight];
      }
      
      // Add Friday trends
      if (day === 5) {
        trends = [...trends, ...config.trendingConfig.friday];
      }
      
      // Add Ramadan trends if applicable
      if (isRamadan()) {
        trends = [...trends, ...config.trendingConfig.ramadan];
      }
      
      // Randomize and limit
      trends = trends.sort(() => Math.random() - 0.5).slice(0, 5);
      setTrendingHashtags(trends);
    } catch (error) {
      console.error('Error fetching trends:', error);
    } finally {
      setIsLoadingTrends(false);
    }
  };

  // Render prompt template with user data
  const renderPromptTemplate = (template: string, data: FormData): string => {
    let prompt = template;
    Object.entries(data).forEach(([key, value]) => {
      prompt = prompt.replace(new RegExp(`{{${key}}}`, 'g'), String(value));
    });
    return prompt;
  };

  // Generate hashtags based on tiers
  const generateHashtags = (content: string, formData: FormData): string[] => {
    const hashtags: string[] = [];
    const config = defaultConfigJson.hashtagConfig;
    
    // Tier 0: Trending hashtags
    hashtags.push(...trendingHashtags);
    
    // Tier 1: High-volume hashtags
    hashtags.push(...config.baseHashtags.tier1_highVolume);
    
    // Tier 2: Cuisine-specific hashtags
    const cuisine = formData.cuisine?.toString().toLowerCase();
    if (cuisine && config.baseHashtags.tier2_cuisine[cuisine]) {
      hashtags.push(...config.baseHashtags.tier2_cuisine[cuisine]);
    }
    
    // Tier 3: Location-specific hashtags
    const location = formData.location?.toString().toLowerCase();
    Object.entries(config.baseHashtags.tier3_location).forEach(([key, tags]) => {
      if (location && location.includes(key)) {
        hashtags.push(...(tags as string[]));
      }
    });
    
    // Tier 4: Occasion-specific hashtags
    if (selectedPrompt.includes('ramadan')) {
      hashtags.push(...config.baseHashtags.tier4_occasion.ramadan);
    } else if (selectedPrompt.includes('nationalDay')) {
      hashtags.push(...config.baseHashtags.tier4_occasion.nationalDay);
    } else {
      hashtags.push(...config.baseHashtags.tier4_occasion.weekend);
    }
    
    // Remove duplicates and limit
    return [...new Set(hashtags)].slice(0, config.maxHashtags);
  };

  // Handle content generation
  const handleGenerate = async () => {
    if (!selectedGoal || !selectedPrompt) {
      alert('Please select a goal and prompt first');
      return;
    }
    
    setIsGenerating(true);
    try {
      // Get the prompt template
      const promptTemplate = config.promptsData[selectedGoal].prompts[selectedPrompt].prompt;
      const fullPrompt = renderPromptTemplate(promptTemplate, formData);
      
      // Simulate AI generation (replace with actual Gemini API call)
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock generated content
      const mockContent = `🌟 ${formData.dishName || 'Special'} Alert! 🌟\n\n` +
        `Join us at ${formData.restaurantName || 'our restaurant'} for an unforgettable experience! ` +
        `${formData.dishDescription || 'Amazing flavors await you.'}\n\n` +
        `📍 ${formData.location || 'Kuwait'}\n` +
        `💰 Only ${formData.price || 'X'} KD\n\n` +
        `Reserve your table now! 📞\n\n`;
      
      setGeneratedContent(mockContent);
      
      // Generate hashtags
      const hashtags = generateHashtags(mockContent, formData);
      setGeneratedHashtags(hashtags);
      
      setActiveTab(1); // Switch to output tab
    } catch (error) {
      console.error('Generation error:', error);
      alert('Failed to generate content. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Handle config upload
  const handleConfigUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const newConfig = JSON.parse(e.target?.result as string);
          setConfig(newConfig);
          alert('Configuration loaded successfully!');
        } catch (error) {
          alert('Invalid configuration file');
        }
      };
      reader.readAsText(file);
    }
  };

  // Handle config download
  const handleConfigDownload = () => {
    const dataStr = JSON.stringify(config, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = 'kuwait-social-ai-config.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Copy content to clipboard
  const handleCopy = () => {
    const fullContent = generatedContent + '\n\n' + generatedHashtags.join(' ');
    navigator.clipboard.writeText(fullContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Get best posting times
  const getBestPostingTimes = () => {
    const scheduleConfig = isRamadan() ? config.schedulingConfig.ramadan : config.schedulingConfig.regular;
    return scheduleConfig.bestTimes;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" fontWeight="bold">
          Smart Post Creator
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <input
            type="file"
            accept=".json"
            onChange={handleConfigUpload}
            style={{ display: 'none' }}
            id="config-upload"
          />
          <label htmlFor="config-upload">
            <Button variant="outlined" component="span" startIcon={<Upload />}>
              Upload Config
            </Button>
          </label>
          <Button variant="outlined" startIcon={<Download />} onClick={handleConfigDownload}>
            Download Config
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Left Column - Controls */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Create Your Post
              </Typography>
              
              {/* Step 1: Choose Goal */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Step 1: Choose Your Goal
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {Object.entries(config.promptsData).map(([key, goal]: [string, any]) => (
                    <Chip
                      key={key}
                      label={`${goal.icon} ${goal.title}`}
                      onClick={() => {
                        setSelectedGoal(key);
                        setSelectedPrompt('');
                        setFormData({});
                      }}
                      color={selectedGoal === key ? 'primary' : 'default'}
                      variant={selectedGoal === key ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Box>

              {/* Step 2: Select Prompt */}
              {selectedGoal && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Step 2: Select a Prompt
                  </Typography>
                  <FormControl fullWidth>
                    <InputLabel>Choose a prompt template</InputLabel>
                    <Select
                      value={selectedPrompt}
                      onChange={(e) => {
                        setSelectedPrompt(e.target.value);
                        setFormData({});
                      }}
                      label="Choose a prompt template"
                    >
                      {Object.entries(config.promptsData[selectedGoal].prompts).map(([key, prompt]: [string, any]) => (
                        <MenuItem key={key} value={key}>
                          {prompt.title}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>
              )}

              {/* Step 3: Fill Details */}
              {selectedPrompt && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Step 3: Fill in the Details
                  </Typography>
                  {config.promptsData[selectedGoal].prompts[selectedPrompt].inputs.map((input: any) => (
                    <Box key={input.id} sx={{ mb: 2 }}>
                      {input.type === 'select' ? (
                        <FormControl fullWidth>
                          <InputLabel>{input.label}</InputLabel>
                          <Select
                            value={formData[input.id] || ''}
                            onChange={(e) => setFormData({ ...formData, [input.id]: e.target.value })}
                            label={input.label}
                            required={input.required}
                          >
                            {input.options.map((option: string) => (
                              <MenuItem key={option} value={option}>
                                {option}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      ) : (
                        <TextField
                          fullWidth
                          type={input.type}
                          label={input.label}
                          placeholder={input.placeholder}
                          value={formData[input.id] || ''}
                          onChange={(e) => setFormData({ ...formData, [input.id]: e.target.value })}
                          required={input.required}
                          multiline={input.type === 'textarea'}
                          rows={input.type === 'textarea' ? 3 : 1}
                        />
                      )}
                    </Box>
                  ))}
                  
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<AutoAwesome />}
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    sx={{ mt: 2 }}
                  >
                    {isGenerating ? 'Generating...' : 'Generate Content'}
                  </Button>
                </Box>
              )}

              {/* Trending Hashtags */}
              <Divider sx={{ my: 3 }} />
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    <TrendingUp sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }} />
                    Live Kuwait Trends
                  </Typography>
                  <IconButton size="small" onClick={fetchTrendingHashtags} disabled={isLoadingTrends}>
                    <Refresh />
                  </IconButton>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {isLoadingTrends ? (
                    <CircularProgress size={20} />
                  ) : (
                    trendingHashtags.map((tag) => (
                      <Chip
                        key={tag}
                        label={tag}
                        size="small"
                        sx={{
                          backgroundColor: '#FFE5E5',
                          color: '#FF6B6B',
                          '& .MuiChip-label': { fontWeight: 500 }
                        }}
                      />
                    ))
                  )}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column - Output */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
                <Tab label="Generated Content" />
                <Tab label="Smart Schedule" />
              </Tabs>

              {/* Generated Content Tab */}
              {activeTab === 0 && (
                <Box sx={{ mt: 3 }}>
                  {generatedContent ? (
                    <>
                      <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                          {generatedContent}
                        </Typography>
                      </Paper>
                      
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Generated Hashtags ({generatedHashtags.length})
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 2 }}>
                        {generatedHashtags.map((tag, index) => {
                          const isTrending = trendingHashtags.includes(tag);
                          return (
                            <Chip
                              key={`${tag}-${index}`}
                              label={tag}
                              size="small"
                              icon={isTrending ? <TrendingUp sx={{ fontSize: 16 }} /> : undefined}
                              sx={{
                                backgroundColor: isTrending ? '#FFE5E5' : undefined,
                                color: isTrending ? '#FF6B6B' : undefined,
                              }}
                            />
                          );
                        })}
                      </Box>
                      
                      <Button
                        fullWidth
                        variant="contained"
                        startIcon={copied ? <Check /> : <ContentCopy />}
                        onClick={handleCopy}
                        color={copied ? 'success' : 'primary'}
                      >
                        {copied ? 'Copied!' : 'Copy All'}
                      </Button>
                    </>
                  ) : (
                    <Alert severity="info">
                      Generated content will appear here
                    </Alert>
                  )}
                </Box>
              )}

              {/* Smart Schedule Tab */}
              {activeTab === 1 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Best Times to Post {isRamadan() && '(Ramadan Schedule)'}
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {getBestPostingTimes().map((time) => (
                      <Paper key={time.time} sx={{ p: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Typography variant="h6">{time.icon}</Typography>
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle2">{time.time}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {time.label}
                            </Typography>
                          </Box>
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<Schedule />}
                          >
                            Schedule
                          </Button>
                        </Box>
                      </Paper>
                    ))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};