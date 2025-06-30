// Application constants for Kuwait Social AI

// Platform configurations
export const PLATFORMS = {
  INSTAGRAM: 'instagram',
  SNAPCHAT: 'snapchat',
  TWITTER: 'twitter',
  LINKEDIN: 'linkedin',
  TIKTOK: 'tiktok',
} as const;

export const PLATFORM_LABELS = {
  [PLATFORMS.INSTAGRAM]: 'Instagram',
  [PLATFORMS.SNAPCHAT]: 'Snapchat',
  [PLATFORMS.TWITTER]: 'Twitter',
  [PLATFORMS.LINKEDIN]: 'LinkedIn',
  [PLATFORMS.TIKTOK]: 'TikTok',
} as const;

export const PLATFORM_COLORS = {
  [PLATFORMS.INSTAGRAM]: '#E4405F',
  [PLATFORMS.SNAPCHAT]: '#FFFC00',
  [PLATFORMS.TWITTER]: '#1DA1F2',
  [PLATFORMS.LINKEDIN]: '#0077B5',
  [PLATFORMS.TIKTOK]: '#000000',
} as const;

// Post statuses
export const POST_STATUS = {
  DRAFT: 'draft',
  SCHEDULED: 'scheduled',
  PUBLISHING: 'publishing',
  PUBLISHED: 'published',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
  EXPIRED: 'expired',
} as const;

export const POST_STATUS_LABELS = {
  [POST_STATUS.DRAFT]: 'Draft',
  [POST_STATUS.SCHEDULED]: 'Scheduled',
  [POST_STATUS.PUBLISHING]: 'Publishing',
  [POST_STATUS.PUBLISHED]: 'Published',
  [POST_STATUS.FAILED]: 'Failed',
  [POST_STATUS.CANCELLED]: 'Cancelled',
  [POST_STATUS.EXPIRED]: 'Expired',
} as const;

export const POST_STATUS_COLORS = {
  [POST_STATUS.DRAFT]: '#757575',
  [POST_STATUS.SCHEDULED]: '#FF9800',
  [POST_STATUS.PUBLISHING]: '#2196F3',
  [POST_STATUS.PUBLISHED]: '#4CAF50',
  [POST_STATUS.FAILED]: '#F44336',
  [POST_STATUS.CANCELLED]: '#9E9E9E',
  [POST_STATUS.EXPIRED]: '#FF5722',
} as const;

// Content types
export const CONTENT_TYPES = {
  POST: 'post',
  STORY: 'story',
  REEL: 'reel',
  CAROUSEL: 'carousel',
} as const;

export const CONTENT_TONES = {
  PROFESSIONAL: 'professional',
  CASUAL: 'casual',
  FRIENDLY: 'friendly',
  AUTHORITATIVE: 'authoritative',
  PLAYFUL: 'playful',
  INSPIRATIONAL: 'inspirational',
  EDUCATIONAL: 'educational',
  URGENT: 'urgent',
} as const;

// User roles
export const USER_ROLES = {
  ADMIN: 'admin',
  CLIENT: 'client',
} as const;

// Kuwait-specific constants
export const KUWAIT_TIMEZONE = 'Asia/Kuwait';

export const PRAYER_TIMES = {
  FAJR: 'fajr',
  DHUHR: 'dhuhr',
  ASR: 'asr',
  MAGHRIB: 'maghrib',
  ISHA: 'isha',
} as const;

export const PRAYER_TIME_LABELS = {
  [PRAYER_TIMES.FAJR]: 'الفجر / Fajr',
  [PRAYER_TIMES.DHUHR]: 'الظهر / Dhuhr',
  [PRAYER_TIMES.ASR]: 'العصر / Asr',
  [PRAYER_TIMES.MAGHRIB]: 'المغرب / Maghrib',
  [PRAYER_TIMES.ISHA]: 'العشاء / Isha',
} as const;

export const KUWAIT_BUSINESS_DAYS = [
  'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'
] as const;

export const ARABIC_MONTHS = [
  'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
  'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
] as const;

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
    CHANGE_PASSWORD: '/auth/change-password',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  POSTS: {
    LIST: '/client/posts',
    CREATE: '/client/posts',
    UPDATE: (id: number) => `/client/posts/${id}`,
    DELETE: (id: number) => `/client/posts/${id}`,
    SCHEDULE: (id: number) => `/client/posts/${id}/schedule`,
    PUBLISH: (id: number) => `/client/posts/${id}/publish`,
    ANALYTICS: (id: number) => `/client/posts/${id}/analytics`,
  },
  CONTENT: {
    GENERATE: '/content/generate',
    GENERATE_FROM_IMAGE: '/content/generate-from-image',
    ENHANCE: '/content/enhance',
  },
  ANALYTICS: {
    DASHBOARD: '/client/analytics/dashboard',
    POSTS: '/client/analytics/posts',
    ENGAGEMENT: '/client/analytics/engagement',
  },
  COMPETITORS: {
    LIST: '/client/competitors',
    CREATE: '/client/competitors',
    UPDATE: (id: number) => `/client/competitors/${id}`,
    DELETE: (id: number) => `/client/competitors/${id}`,
    ANALYZE: (id: number) => `/client/competitors/${id}/analyze`,
    COMPARE: '/client/competitors/compare',
  },
  FEATURES: {
    PRAYER_TIMES: '/prayer-times',
    HOLIDAYS: '/kuwait-holidays',
    HASHTAG_SUGGESTIONS: '/features/hashtag-suggestions',
  },
} as const;

// Validation constants
export const VALIDATION = {
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD_MIN_LENGTH: 8,
  POST_CAPTION_MAX_LENGTH: 2200,
  HASHTAG_MAX_COUNT: 30,
  FILE_SIZE_LIMIT: 10 * 1024 * 1024, // 10MB
  SUPPORTED_IMAGE_TYPES: ['.jpeg', '.jpg', '.png', '.gif', '.webp'],
  SUPPORTED_VIDEO_TYPES: ['.mp4', '.mov', '.avi'],
} as const;

// UI constants
export const DRAWER_WIDTH = 280;
export const DRAWER_WIDTH_COLLAPSED = 64;
export const HEADER_HEIGHT = 64;
export const MOBILE_BREAKPOINT = 768;

export const NOTIFICATION_DURATION = {
  SUCCESS: 4000,
  ERROR: 8000,
  WARNING: 6000,
  INFO: 5000,
} as const;

// Date/time formats
export const DATE_FORMATS = {
  DISPLAY: 'MMM dd, yyyy',
  DISPLAY_WITH_TIME: 'MMM dd, yyyy HH:mm',
  API: 'yyyy-MM-dd',
  API_WITH_TIME: "yyyy-MM-dd'T'HH:mm:ssxxx",
  TIME_ONLY: 'HH:mm',
  RELATIVE: 'relative', // for relative time like "2 hours ago"
} as const;

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your internet connection.',
  UNAUTHORIZED: 'Your session has expired. Please login again.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'An internal server error occurred. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  FILE_TOO_LARGE: 'File size is too large. Maximum size is 10MB.',
  UNSUPPORTED_FILE_TYPE: 'Unsupported file type.',
  CONTENT_GENERATION_FAILED: 'Failed to generate content. Please try again.',
  TRANSLATION_FAILED: 'Translation service is temporarily unavailable.',
} as const;

// Success messages
export const SUCCESS_MESSAGES = {
  POST_CREATED: 'Post created successfully',
  POST_UPDATED: 'Post updated successfully',
  POST_DELETED: 'Post deleted successfully',
  POST_SCHEDULED: 'Post scheduled successfully',
  POST_PUBLISHED: 'Post published successfully',
  CONTENT_GENERATED: 'Content generated successfully',
  PASSWORD_CHANGED: 'Password changed successfully',
  SETTINGS_SAVED: 'Settings saved successfully',
  COMPETITOR_ADDED: 'Competitor added successfully',
  ANALYSIS_COMPLETED: 'Analysis completed successfully',
} as const;