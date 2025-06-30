// API response types for Kuwait Social AI

export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

export interface PaginationParams {
  page?: number;
  per_page?: number;
}

export interface PaginationResponse {
  page: number;
  per_page: number;
  total: number;
  pages: number;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// Authentication types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface TokenRefreshResponse {
  access_token: string;
}

// User and Client types
export interface User {
  id: number;
  email: string;
  role: 'admin' | 'client';
  is_active: boolean;
  created_at: string;
}

export interface Client {
  id: number;
  user_id: number;
  business_name: string;
  industry: string;
  subscription_status: 'active' | 'inactive' | 'trial';
  is_active: boolean;
  created_at: string;
}

// Post types
export interface PostDraft {
  caption: string;
  caption_ar?: string;
  hashtags: string[];
  platform: string[];
  scheduled_time?: string;
  media_files?: any[];
}

export interface Post {
  id: number;
  client_id: number;
  caption: string;
  caption_ar?: string;
  hashtags: string[];
  platform?: string[];
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  scheduled_time?: string;
  published_at?: string;
  created_at: string;
  analytics?: PostAnalytics;
  metrics?: {
    likes: number;
    comments: number;
    shares: number;
  };
  media_files?: any[];
}

export interface PostAnalytics {
  id: number;
  post_id: number;
  platform: string;
  likes: number;
  comments: number;
  shares: number;
  reach: number;
  impressions: number;
  engagement_rate: number;
  recorded_at: string;
}

// Content generation types
export interface ContentGenerationRequest {
  prompt: string;
  include_arabic?: boolean;
  platform?: string;
  content_type?: string;
  tone?: string;
  include_hashtags?: boolean;
}

export interface GeneratedContent {
  caption_en: string;
  caption_ar?: string;
  hashtags: string[];
  metadata: {
    generated_at: string;
    platform: string;
    ai_model: string;
    tone: string;
  };
  translation_warning?: {
    message: string;
    suggestion: string;
  };
}

// Analytics types
export interface AnalyticsMetrics {
  total_posts: number;
  total_engagement: number;
  avg_engagement_rate: number;
  follower_growth: number;
  top_performing_posts: Post[];
  engagement_by_platform: Record<string, number>;
}

// Competitor types
export interface Competitor {
  id: number;
  client_id: number;
  name: string;
  username: string;
  platform: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  latest_analysis?: CompetitorAnalysis;
}

export interface CompetitorAnalysis {
  id: number;
  competitor_id: number;
  followers_count: number;
  following_count: number;
  posts_count: number;
  engagement_rate: number;
  avg_likes_per_post: number;
  avg_comments_per_post: number;
  posting_frequency: Record<string, any>;
  best_posting_times: string[];
  top_hashtags: string[];
  content_themes: string[];
  analysis_date: string;
}

// Kuwait-specific features
export interface PrayerTimes {
  fajr: string;
  dhuhr: string;
  asr: string;
  maghrib: string;
  isha: string;
  date: string;
}

export interface KuwaitHoliday {
  date: string;
  name: string;
  type: 'public' | 'national' | 'religious';
}

// Campaign types
export interface Campaign {
  id: number;
  client_id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  status: 'draft' | 'active' | 'completed' | 'paused';
  budget?: number;
  target_audience: string;
  goals: string[];
  created_at: string;
}

// Error logging types
export interface ErrorLog {
  message: string;
  stack?: string;
  url: string;
  userAgent: string;
  timestamp: string;
  userId?: number;
  level: 'error' | 'warning' | 'info';
  metadata?: Record<string, any>;
}

// Analytics Dashboard types
export interface AnalyticsData {
  dateRange: {
    start: string;
    end: string;
  };
  platforms: PlatformMetrics[];
  totals: {
    impressions: number;
    reach: number;
    engagement: number;
    followers: number;
  };
  trends: TrendData[];
}

export interface PlatformMetrics {
  platform: string;
  metrics: {
    impressions: number;
    reach: number;
    engagement: number;
    followers: number;
    posts: number;
  };
}

export interface TrendData {
  date: string;
  instagram?: MetricPoint;
  twitter?: MetricPoint;
  snapchat?: MetricPoint;
}

export interface MetricPoint {
  impressions: number;
  reach: number;
  engagement: number;
  followers: number;
}