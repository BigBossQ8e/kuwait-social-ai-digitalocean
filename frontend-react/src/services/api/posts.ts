// Posts API endpoints

import { api } from './baseApi';
import type { 
  Post, 
  PostDraft, 
  PaginationParams, 
  PaginationResponse,
  GeneratedContent,
  ContentGenerationRequest,
  PostAnalytics
} from '../../types/api.types';

export const postsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getPosts: builder.query<
      { posts: Post[]; pagination: PaginationResponse },
      PaginationParams & { status?: string; platform?: string }
    >({
      query: (params) => ({
        url: '/client/posts',
        params,
      }),
      providesTags: ['Post' as const],
    }),
    
    getPost: builder.query<Post, number>({
      query: (id) => `/client/posts/${id}`,
      providesTags: (_, __, id) => [{ type: 'Post' as const, id }],
    }),
    
    createPost: builder.mutation<Post, PostDraft>({
      query: (post) => ({
        url: '/client/posts',
        method: 'POST',
        body: post,
      }),
      invalidatesTags: ['Post' as const],
    }),
    
    updatePost: builder.mutation<Post, { id: number; data: Partial<PostDraft> }>({
      query: ({ id, data }) => ({
        url: `/client/posts/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'Post' as const, id }],
    }),
    
    deletePost: builder.mutation<{ message: string }, number>({
      query: (id) => ({
        url: `/client/posts/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Post' as const],
    }),
    
    schedulePost: builder.mutation<
      Post,
      { id: number; scheduled_time: string; platforms: string[] }
    >({
      query: ({ id, ...body }) => ({
        url: `/client/posts/${id}/schedule`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'Post' as const, id }],
    }),
    
    publishPost: builder.mutation<Post, { id: number; platforms: string[] }>({
      query: ({ id, platforms }) => ({
        url: `/client/posts/${id}/publish`,
        method: 'POST',
        body: { platforms },
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'Post' as const, id }],
    }),
    
    generateContent: builder.mutation<GeneratedContent, ContentGenerationRequest>({
      query: (request) => ({
        url: '/content/generate',
        method: 'POST',
        body: request,
      }),
    }),
    
    generateFromImage: builder.mutation<
      GeneratedContent,
      { image_url: string; include_arabic?: boolean; platform?: string }
    >({
      query: (body) => ({
        url: '/content/generate-from-image',
        method: 'POST',
        body,
      }),
    }),
    
    enhanceContent: builder.mutation<
      { enhanced_content: string },
      { content: string; improvements: string[] }
    >({
      query: (body) => ({
        url: '/content/enhance',
        method: 'POST',
        body,
      }),
    }),
    
    getPostAnalytics: builder.query<
      PostAnalytics[],
      { post_id: number; platform?: string }
    >({
      query: (params) => ({
        url: `/client/posts/${params.post_id}/analytics`,
        params: params.platform ? { platform: params.platform } : {},
      }),
      providesTags: (_, __, { post_id }) => [
        { type: 'Analytics' as const, id: `post-${post_id}` }
      ],
    }),
    
    getScheduledPosts: builder.query<
      { posts: Post[]; pagination: PaginationResponse },
      PaginationParams & { date_from?: string; date_to?: string }
    >({
      query: (params) => ({
        url: '/client/posts/scheduled',
        params,
      }),
      providesTags: ['Post' as const],
    }),
    
    cancelScheduledPost: builder.mutation<{ message: string }, number>({
      query: (id) => ({
        url: `/client/posts/${id}/cancel`,
        method: 'POST',
      }),
      invalidatesTags: (_, __, id) => [{ type: 'Post' as const, id }],
    }),
    
    duplicatePost: builder.mutation<Post, number>({
      query: (id) => ({
        url: `/client/posts/${id}/duplicate`,
        method: 'POST',
      }),
      invalidatesTags: ['Post' as const],
    }),
    
    bulkSchedule: builder.mutation<
      { success_count: number; failed_count: number; details: any[] },
      { post_ids: number[]; schedule_data: any }
    >({
      query: (body) => ({
        url: '/client/posts/bulk-schedule',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Post' as const],
    }),
  }),
});

export const {
  useGetPostsQuery,
  useGetPostQuery,
  useCreatePostMutation,
  useUpdatePostMutation,
  useDeletePostMutation,
  useSchedulePostMutation,
  usePublishPostMutation,
  useGenerateContentMutation,
  useGenerateFromImageMutation,
  useEnhanceContentMutation,
  useGetPostAnalyticsQuery,
  useGetScheduledPostsQuery,
  useCancelScheduledPostMutation,
  useDuplicatePostMutation,
  useBulkScheduleMutation,
} = postsApi;