// Posts API endpoints using centralized API client
import api from '../apiClient';
import type { 
  Post, 
  PostDraft, 
  CreatePostData, 
  UpdatePostData,
  PostsResponse,
  PostFilters 
} from '../types/posts';

export const postsApi = {
  // Get all posts with pagination and filters
  getPosts: (params?: PostFilters) =>
    api.get<PostsResponse>('/posts', { params }),

  // Get single post by ID
  getPost: (id: number) =>
    api.get<Post>(`/posts/${id}`),

  // Create new post
  createPost: (data: CreatePostData) =>
    api.post<Post>('/posts', data),

  // Update existing post
  updatePost: (id: number, data: UpdatePostData) =>
    api.put<Post>(`/posts/${id}`, data),

  // Delete post
  deletePost: (id: number) =>
    api.delete(`/posts/${id}`),

  // Schedule post
  schedulePost: (id: number, scheduledFor: string) =>
    api.post<Post>(`/posts/${id}/schedule`, { scheduled_for: scheduledFor }),

  // Publish post immediately
  publishPost: (id: number) =>
    api.post<Post>(`/posts/${id}/publish`),

  // Get post drafts
  getDrafts: () =>
    api.get<PostDraft[]>('/posts/drafts'),

  // Save draft
  saveDraft: (data: Partial<CreatePostData>) =>
    api.post<PostDraft>('/posts/drafts', data),

  // Upload media for post
  uploadMedia: (file: File, onProgress?: (progress: number) => void) =>
    api.uploadFile<{ url: string; thumbnail?: string }>('/posts/media', file, onProgress),

  // Generate AI content
  generateContent: (prompt: string, platform: string) =>
    api.post<{ content: string; hashtags: string[] }>('/posts/generate', {
      prompt,
      platform,
    }),

  // Get suggested hashtags
  getSuggestedHashtags: (content: string, platform: string) =>
    api.post<string[]>('/posts/hashtags/suggest', {
      content,
      platform,
    }),

  // Preview post
  previewPost: (data: CreatePostData) =>
    api.post<{ preview_url: string }>('/posts/preview', data),
};