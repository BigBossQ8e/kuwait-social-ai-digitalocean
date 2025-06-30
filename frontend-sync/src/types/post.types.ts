// Post and content types for Kuwait Social AI

export interface PostDraft {
  caption: string;
  caption_ar?: string;
  hashtags: string[];
  platform: Platform[];
  media_files?: MediaFile[];
  scheduled_time?: Date;
  campaign_id?: number;
  location?: string;
  target_audience?: string;
  content_warnings?: string[];
}

export interface PostData extends PostDraft {
  id: number;
  client_id: number;
  status: PostStatus;
  created_at: string;
  updated_at: string;
  published_at?: string;
  analytics?: PostAnalytics[];
  approval_status?: ApprovalStatus;
  ai_generated?: boolean;
  ai_metadata?: AIGenerationMetadata;
}

export type Platform = 'instagram' | 'snapchat' | 'twitter' | 'linkedin' | 'tiktok';

export type PostStatus = 
  | 'draft' 
  | 'scheduled' 
  | 'publishing' 
  | 'published' 
  | 'failed' 
  | 'cancelled'
  | 'expired';

export type ApprovalStatus = 
  | 'pending_review' 
  | 'approved' 
  | 'rejected' 
  | 'needs_revision';

export interface MediaFile {
  id: string;
  type: 'image' | 'video' | 'gif';
  url: string;
  thumbnail_url?: string;
  filename: string;
  size: number;
  dimensions?: {
    width: number;
    height: number;
  };
  duration?: number; // for videos
  alt_text?: string;
  processing_status?: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface PostAnalytics {
  id: number;
  post_id: number;
  platform: Platform;
  metrics: PlatformMetrics;
  recorded_at: string;
  is_final: boolean; // true if no more updates expected
}

export interface PlatformMetrics {
  likes: number;
  comments: number;
  shares: number;
  saves?: number; // Instagram
  views?: number; // Stories, Reels, Videos
  reach: number;
  impressions: number;
  engagement_rate: number;
  click_through_rate?: number;
  story_replies?: number; // Instagram Stories
  story_exits?: number; // Instagram Stories
  profile_visits?: number;
  website_clicks?: number;
  email_contacts?: number;
  direction_requests?: number;
  call_clicks?: number;
}

export interface AIGenerationMetadata {
  model: string;
  prompt: string;
  temperature: number;
  generated_at: string;
  content_type: 'post' | 'story' | 'reel' | 'carousel';
  tone: string;
  target_audience: string;
  keywords: string[];
  moderation_passed: boolean;
  moderation_score?: number;
  translation_service?: 'google' | 'openai' | 'manual';
}

export interface ContentTemplate {
  id: number;
  client_id: number;
  name: string;
  category: ContentCategory;
  template_text: string;
  template_text_ar?: string;
  default_hashtags: string[];
  suggested_media_type: 'image' | 'video' | 'carousel' | 'any';
  industry_tags: string[];
  tone: ContentTone;
  is_active: boolean;
  usage_count: number;
  created_at: string;
}

export type ContentCategory = 
  | 'product_announcement'
  | 'customer_testimonial'
  | 'behind_the_scenes'
  | 'educational'
  | 'promotional'
  | 'seasonal'
  | 'event'
  | 'company_news'
  | 'industry_insights'
  | 'user_generated_content';

export type ContentTone = 
  | 'professional'
  | 'casual'
  | 'friendly'
  | 'authoritative'
  | 'playful'
  | 'inspirational'
  | 'educational'
  | 'urgent';

export interface PostSchedule {
  id: number;
  client_id: number;
  name: string;
  posts: ScheduledPost[];
  recurring: boolean;
  recurrence_pattern?: RecurrencePattern;
  timezone: string;
  is_active: boolean;
  created_at: string;
}

export interface ScheduledPost {
  id: string;
  post_draft: PostDraft;
  scheduled_time: Date;
  status: PostStatus;
  retry_count: number;
  last_attempt?: string;
  error_message?: string;
}

export interface RecurrencePattern {
  type: 'daily' | 'weekly' | 'monthly';
  interval: number; // every N days/weeks/months
  days_of_week?: number[]; // 0=Sunday, 1=Monday, etc.
  day_of_month?: number;
  end_date?: Date;
  max_occurrences?: number;
}

export interface HashtagSuggestion {
  hashtag: string;
  popularity_score: number;
  engagement_potential: number;
  relevance_score: number;
  trending: boolean;
  category: 'general' | 'local' | 'industry' | 'branded';
  usage_count_last_30_days: number;
}

export interface ContentInsights {
  best_posting_times: {
    platform: Platform;
    day_of_week: string;
    hour: number;
    engagement_score: number;
  }[];
  top_performing_hashtags: {
    hashtag: string;
    avg_engagement: number;
    posts_used: number;
  }[];
  content_performance_by_type: {
    content_type: ContentCategory;
    avg_engagement: number;
    total_posts: number;
  }[];
  audience_demographics: {
    age_groups: Record<string, number>;
    gender_distribution: Record<string, number>;
    location_breakdown: Record<string, number>;
    interests: string[];
  };
}