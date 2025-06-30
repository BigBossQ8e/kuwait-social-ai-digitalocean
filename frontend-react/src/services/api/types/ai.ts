/**
 * AI Content Generation API types
 */

export interface ContentGenerationRequest {
  prompt: string;
  platform?: 'instagram' | 'twitter' | 'snapchat' | 'tiktok';
  tone?: 'professional' | 'casual' | 'enthusiastic' | 'formal';
  include_arabic?: boolean;
  include_hashtags?: boolean;
  business_type?: string;
  additional_context?: {
    target_audience?: string;
    campaign_goal?: string;
    key_message?: string;
  };
}

export interface ContentGenerationResponse {
  success: boolean;
  data: {
    content: string;
    platform: string;
    tone: string;
    character_count: number;
    arabic_content?: string;
    hashtags?: string[];
    recommendations?: string[];
    optimal_posting_times?: {
      weekdays: {
        morning?: string[];
        evening?: string[];
      };
      weekends: {
        morning?: string[];
        evening?: string[];
      };
      avoid?: string[];
      best_days?: string[];
    };
    usage?: {
      posts_used: number;
      posts_limit: number;
      posts_remaining: number;
    };
  };
}

export interface TranslationRequest {
  text: string;
  source_lang?: string;
  target_lang?: string;
}

export interface TranslationResponse {
  success: boolean;
  data: {
    original_text: string;
    translated_text: string;
    source_lang: string;
    target_lang: string;
  };
}

export interface HashtagGenerationRequest {
  content: string;
  platform?: string;
  business_type?: string;
}

export interface HashtagGenerationResponse {
  success: boolean;
  data: {
    hashtags: {
      high_volume: string[];
      medium_volume: string[];
      niche: string[];
      all: string[];
    };
    total_count: number;
    platform: string;
  };
}

export interface ContentEnhancementRequest {
  content: string;
  enhancement_type: 'grammar' | 'tone' | 'engagement' | 'localization';
}

export interface ContentEnhancementResponse {
  success: boolean;
  data: {
    enhanced_content: string;
    original_content: string;
    changes: string[];
    suggestions: string[];
    enhancement_type: string;
    error?: string;
  };
}

export interface ContentTemplate {
  id: number;
  name: string;
  prompt: string;
  example: string;
  tags: string[];
}

export interface TrendingTopic {
  topic: string;
  description: string;
  relevance: 'high' | 'medium' | 'low';
  hashtags: string[];
}

export interface TrendingData {
  topics: TrendingTopic[];
  hashtags: {
    trending_now: string[];
    evergreen: string[];
    seasonal: string[];
  };
  updated_at: string;
}