// Post-related types
export interface Post {
  id: number;
  client_id: number;
  platform: Platform;
  content: string;
  media_urls?: string[];
  hashtags?: string[];
  status: PostStatus;
  scheduled_for?: string;
  published_at?: string;
  engagement_metrics?: EngagementMetrics;
  created_at: string;
  updated_at: string;
  created_by: number;
  client?: {
    id: number;
    name: string;
    logo?: string;
  };
}

export interface PostDraft {
  id: number;
  client_id?: number;
  platform?: Platform;
  content?: string;
  media_urls?: string[];
  hashtags?: string[];
  created_at: string;
  updated_at: string;
}

export interface CreatePostData {
  client_id: number;
  platform: Platform;
  content: string;
  media_urls?: string[];
  hashtags?: string[];
  scheduled_for?: string;
}

export interface UpdatePostData {
  content?: string;
  media_urls?: string[];
  hashtags?: string[];
  scheduled_for?: string;
}

export interface PostsResponse {
  posts: Post[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface PostFilters {
  page?: number;
  per_page?: number;
  client_id?: number;
  platform?: Platform;
  status?: PostStatus;
  date_from?: string;
  date_to?: string;
  search?: string;
}

export interface EngagementMetrics {
  likes: number;
  comments: number;
  shares: number;
  reach: number;
  impressions: number;
  engagement_rate: number;
}

export type Platform = 'instagram' | 'twitter' | 'facebook' | 'linkedin' | 'tiktok';

export type PostStatus = 'draft' | 'scheduled' | 'published' | 'failed';