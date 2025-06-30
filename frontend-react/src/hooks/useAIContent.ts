/**
 * Custom hook for AI content generation
 */

import { useState, useCallback } from 'react';
import { aiApi } from '../services/api/endpoints/ai';
import type {
  ContentGenerationRequest,
  ContentGenerationResponse,
  TranslationRequest,
  HashtagGenerationRequest,
  ContentEnhancementRequest,
  ContentTemplate,
  TrendingData
} from '../services/api/types/ai';

export interface UseAIContentReturn {
  // States
  loading: boolean;
  error: string | null;
  generatedContent: ContentGenerationResponse['data'] | null;
  translatedText: string | null;
  suggestedHashtags: string[] | null;
  enhancedContent: string | null;
  templates: ContentTemplate[];
  trendingData: TrendingData | null;
  
  // Actions
  generateContent: (request: ContentGenerationRequest) => Promise<void>;
  translateContent: (request: TranslationRequest) => Promise<void>;
  generateHashtags: (request: HashtagGenerationRequest) => Promise<void>;
  enhanceContent: (request: ContentEnhancementRequest) => Promise<void>;
  loadTemplates: (platform?: string, businessType?: string) => Promise<void>;
  loadTrending: () => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

export const useAIContent = (): UseAIContentReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedContent, setGeneratedContent] = useState<ContentGenerationResponse['data'] | null>(null);
  const [translatedText, setTranslatedText] = useState<string | null>(null);
  const [suggestedHashtags, setSuggestedHashtags] = useState<string[] | null>(null);
  const [enhancedContent, setEnhancedContent] = useState<string | null>(null);
  const [templates, setTemplates] = useState<ContentTemplate[]>([]);
  const [trendingData, setTrendingData] = useState<TrendingData | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const reset = useCallback(() => {
    setGeneratedContent(null);
    setTranslatedText(null);
    setSuggestedHashtags(null);
    setEnhancedContent(null);
    setError(null);
  }, []);

  const generateContent = useCallback(async (request: ContentGenerationRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await aiApi.generateContent(request);
      setGeneratedContent(response.data);
      
      // Also set hashtags if they were generated
      if (response.data.hashtags) {
        setSuggestedHashtags(response.data.hashtags);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to generate content';
      setError(errorMessage);
      console.error('Content generation error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const translateContent = useCallback(async (request: TranslationRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await aiApi.translateContent(request);
      setTranslatedText(response.data.translated_text);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to translate content';
      setError(errorMessage);
      console.error('Translation error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const generateHashtags = useCallback(async (request: HashtagGenerationRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await aiApi.generateHashtags(request);
      setSuggestedHashtags(response.data.hashtags.all);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to generate hashtags';
      setError(errorMessage);
      console.error('Hashtag generation error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const enhanceContent = useCallback(async (request: ContentEnhancementRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await aiApi.enhanceContent(request);
      setEnhancedContent(response.data.enhanced_content);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to enhance content';
      setError(errorMessage);
      console.error('Content enhancement error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadTemplates = useCallback(async (platform?: string, businessType?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const loadedTemplates = await aiApi.getTemplates(platform, businessType);
      setTemplates(loadedTemplates);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to load templates';
      setError(errorMessage);
      console.error('Template loading error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadTrending = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await aiApi.getTrending();
      setTrendingData(data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to load trending data';
      setError(errorMessage);
      console.error('Trending data error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    // States
    loading,
    error,
    generatedContent,
    translatedText,
    suggestedHashtags,
    enhancedContent,
    templates,
    trendingData,
    
    // Actions
    generateContent,
    translateContent,
    generateHashtags,
    enhanceContent,
    loadTemplates,
    loadTrending,
    clearError,
    reset
  };
};