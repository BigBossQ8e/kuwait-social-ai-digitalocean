// User-specific types for Kuwait Social AI

export interface UserProfile {
  id: number;
  email: string;
  role: 'admin' | 'client';
  is_active: boolean;
  created_at: string;
  last_login?: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  language: 'en' | 'ar';
  timezone: string;
  notifications: NotificationPreferences;
  dashboard_layout: DashboardLayout[];
  theme: 'light' | 'dark' | 'auto';
}

export interface NotificationPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  notification_types: {
    post_published: boolean;
    engagement_alerts: boolean;
    competitor_updates: boolean;
    system_maintenance: boolean;
    payment_reminders: boolean;
  };
}

export interface DashboardLayout {
  id: string;
  type: 'metrics' | 'recent_posts' | 'analytics' | 'prayer_times' | 'competitors';
  position: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
  visible: boolean;
}

export interface ClientProfile extends UserProfile {
  client: {
    id: number;
    business_name: string;
    industry: string;
    business_type: string;
    location: string;
    website?: string;
    phone?: string;
    subscription_status: 'active' | 'inactive' | 'trial';
    subscription_plan: 'basic' | 'premium' | 'enterprise';
    subscription_expires_at?: string;
    billing_info?: BillingInfo;
    social_accounts: SocialAccount[];
    features_enabled: FeatureFlags;
  };
}

export interface BillingInfo {
  payment_method: 'credit_card' | 'bank_transfer';
  last_payment_date?: string;
  next_payment_date?: string;
  amount: number;
  currency: 'KWD' | 'USD';
}

export interface SocialAccount {
  id: number;
  platform: 'instagram' | 'snapchat' | 'twitter' | 'linkedin';
  username: string;
  account_id: string;
  is_active: boolean;
  connected_at: string;
  last_sync: string;
  follower_count?: number;
  connection_status: 'connected' | 'disconnected' | 'expired';
}

export interface FeatureFlags {
  ai_content_generation: boolean;
  competitor_analysis: boolean;
  advanced_analytics: boolean;
  prayer_time_integration: boolean;
  hashtag_suggestions: boolean;
  auto_posting: boolean;
  bulk_scheduling: boolean;
  custom_branding: boolean;
  api_access: boolean;
  priority_support: boolean;
}

export interface AdminProfile extends UserProfile {
  admin_permissions: AdminPermissions;
  managed_clients: number[];
}

export interface AdminPermissions {
  view_all_clients: boolean;
  modify_client_settings: boolean;
  access_system_metrics: boolean;
  manage_users: boolean;
  view_billing: boolean;
  system_maintenance: boolean;
  content_moderation: boolean;
}