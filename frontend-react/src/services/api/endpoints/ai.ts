/**
 * AI Content Generation API endpoints
 */

import { apiClient } from '../apiClient';
import type {
  ContentGenerationRequest,
  ContentGenerationResponse,
  TranslationRequest,
  TranslationResponse,
  HashtagGenerationRequest,
  HashtagGenerationResponse,
  ContentEnhancementRequest,
  ContentEnhancementResponse,
  ContentTemplate,
  TrendingData
} from '../types/ai';

export const aiApi = {
  /**
   * Generate AI-powered content
   */
  generateContent: async (data: ContentGenerationRequest): Promise<ContentGenerationResponse> => {
    const response = await apiClient.post<ContentGenerationResponse>('/api/ai/generate', data);
    return response.data;
  },

  /**
   * Translate content between languages
   */
  translateContent: async (data: TranslationRequest): Promise<TranslationResponse> => {
    const response = await apiClient.post<TranslationResponse>('/api/ai/translate', data);
    return response.data;
  },

  /**
   * Generate hashtag suggestions
   */
  generateHashtags: async (data: HashtagGenerationRequest): Promise<HashtagGenerationResponse> => {
    const response = await apiClient.post<HashtagGenerationResponse>('/api/ai/hashtags', data);
    return response.data;
  },

  /**
   * Enhance existing content
   */
  enhanceContent: async (data: ContentEnhancementRequest): Promise<ContentEnhancementResponse> => {
    const response = await apiClient.post<ContentEnhancementResponse>('/api/ai/enhance', data);
    return response.data;
  },

  /**
   * Get content templates
   */
  getTemplates: async (platform?: string, businessType?: string): Promise<ContentTemplate[]> => {
    const params = new URLSearchParams();
    if (platform) params.append('platform', platform);
    if (businessType) params.append('business_type', businessType);
    
    const response = await apiClient.get<{ success: boolean; data: { templates: ContentTemplate[] } }>(
      `/api/ai/templates?${params.toString()}`
    );
    return response.data.data.templates;
  },

  /**
   * Get trending topics and hashtags
   */
  getTrending: async (): Promise<TrendingData> => {
    const response = await apiClient.get<{ success: boolean; data: TrendingData }>('/api/ai/trending');
    return response.data.data;
  }
};