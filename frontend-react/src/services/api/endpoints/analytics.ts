// Analytics API endpoints using centralized API client
import api from '../apiClient';
import type {
  AnalyticsOverview,
  EngagementData,
  PlatformMetrics,
  TopPosts,
  AudienceInsights,
  DateRange,
} from '../types/analytics';

export const analyticsApi = {
  // Get analytics overview
  getOverview: (clientId?: number, dateRange?: DateRange) =>
    api.get<AnalyticsOverview>('/analytics/overview', {
      params: { client_id: clientId, ...dateRange },
    }),

  // Get engagement data over time
  getEngagementTrends: (clientId?: number, dateRange?: DateRange) =>
    api.get<EngagementData[]>('/analytics/engagement', {
      params: { client_id: clientId, ...dateRange },
    }),

  // Get platform-specific metrics
  getPlatformMetrics: (platform: string, clientId?: number, dateRange?: DateRange) =>
    api.get<PlatformMetrics>(`/analytics/platforms/${platform}`, {
      params: { client_id: clientId, ...dateRange },
    }),

  // Get top performing posts
  getTopPosts: (clientId?: number, limit = 10) =>
    api.get<TopPosts>('/analytics/top-posts', {
      params: { client_id: clientId, limit },
    }),

  // Get audience insights
  getAudienceInsights: (clientId?: number) =>
    api.get<AudienceInsights>('/analytics/audience', {
      params: { client_id: clientId },
    }),

  // Export analytics report
  exportReport: (format: 'pdf' | 'csv' | 'excel', clientId?: number, dateRange?: DateRange) =>
    api.get<Blob>('/analytics/export', {
      params: { format, client_id: clientId, ...dateRange },
      responseType: 'blob',
    }),

  // Get real-time metrics
  getRealTimeMetrics: (clientId?: number) =>
    api.get<{ active_users: number; recent_posts: number; today_engagement: number }>(
      '/analytics/realtime',
      { params: { client_id: clientId } }
    ),

  // Get content performance analysis
  getContentAnalysis: (clientId?: number, dateRange?: DateRange) =>
    api.get<{
      best_times: Record<string, string[]>;
      top_hashtags: Array<{ tag: string; count: number; engagement: number }>;
      content_types: Array<{ type: string; performance: number }>;
    }>('/analytics/content', {
      params: { client_id: clientId, ...dateRange },
    }),
};