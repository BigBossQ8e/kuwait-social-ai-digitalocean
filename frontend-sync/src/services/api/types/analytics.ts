// Analytics types
export interface AnalyticsOverview {
  total_posts: number;
  total_engagement: number;
  average_engagement_rate: number;
  total_reach: number;
  total_impressions: number;
  growth_rate: number;
  period: {
    start_date: string;
    end_date: string;
  };
}

export interface EngagementData {
  date: string;
  likes: number;
  comments: number;
  shares: number;
  reach: number;
  impressions: number;
  engagement_rate: number;
}

export interface PlatformMetrics {
  platform: string;
  metrics: {
    posts_count: number;
    total_engagement: number;
    average_engagement_rate: number;
    total_reach: number;
    total_impressions: number;
    best_performing_content_type: string;
    peak_engagement_time: string;
  };
  trends: Array<{
    date: string;
    value: number;
    metric: string;
  }>;
}

export interface TopPosts {
  posts: Array<{
    id: number;
    platform: string;
    content: string;
    published_at: string;
    engagement_metrics: {
      likes: number;
      comments: number;
      shares: number;
      engagement_rate: number;
    };
    media_url?: string;
  }>;
}

export interface AudienceInsights {
  demographics: {
    age_groups: Array<{ range: string; percentage: number }>;
    gender: Array<{ type: string; percentage: number }>;
    locations: Array<{ city: string; country: string; percentage: number }>;
  };
  interests: Array<{ category: string; score: number }>;
  active_times: {
    days: Array<{ day: string; activity_score: number }>;
    hours: Array<{ hour: number; activity_score: number }>;
  };
}

export interface DateRange {
  start_date?: string;
  end_date?: string;
  period?: 'day' | 'week' | 'month' | 'quarter' | 'year';
}