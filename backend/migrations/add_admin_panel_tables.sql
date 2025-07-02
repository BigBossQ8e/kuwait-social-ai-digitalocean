-- Admin Panel Database Schema
-- Run this migration to add all admin panel tables

-- Platform Configuration
CREATE TABLE IF NOT EXISTS platform_configs (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) UNIQUE NOT NULL,
    is_enabled BOOLEAN DEFAULT FALSE,
    icon VARCHAR(10),
    display_name VARCHAR(100),
    api_endpoint VARCHAR(500),
    active_clients INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feature Flags
CREATE TABLE IF NOT EXISTS feature_flags (
    id SERIAL PRIMARY KEY,
    feature_key VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    display_name VARCHAR(200),
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    icon VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sub-features
CREATE TABLE IF NOT EXISTS feature_subflags (
    id SERIAL PRIMARY KEY,
    feature_id INTEGER REFERENCES feature_flags(id) ON DELETE CASCADE,
    sub_key VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    is_enabled BOOLEAN DEFAULT TRUE,
    config JSONB,
    UNIQUE(feature_id, sub_key)
);

-- Packages (Enhanced)
CREATE TABLE IF NOT EXISTS packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    description TEXT,
    price_kwd DECIMAL(10,2),
    billing_period VARCHAR(20) DEFAULT 'monthly',
    is_active BOOLEAN DEFAULT TRUE,
    features JSONB,
    limits JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Package Features Mapping
CREATE TABLE IF NOT EXISTS package_features (
    id SERIAL PRIMARY KEY,
    package_id INTEGER REFERENCES packages(id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES feature_flags(id) ON DELETE CASCADE,
    is_included BOOLEAN DEFAULT TRUE,
    custom_config JSONB,
    UNIQUE(package_id, feature_id)
);

-- API Key Configuration
CREATE TABLE IF NOT EXISTS api_configs (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    api_key TEXT, -- Will be encrypted
    api_secret TEXT, -- Will be encrypted
    endpoint VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    monthly_budget DECIMAL(10,2),
    current_usage DECIMAL(10,2) DEFAULT 0,
    last_checked TIMESTAMP,
    health_status VARCHAR(20) DEFAULT 'unknown',
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin Activity Log
CREATE TABLE IF NOT EXISTS admin_activities (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES admins(id),
    action VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id INTEGER,
    changes JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuration History
CREATE TABLE IF NOT EXISTS config_history (
    id SERIAL PRIMARY KEY,
    config_type VARCHAR(50),
    config_id INTEGER,
    previous_value JSONB,
    new_value JSONB,
    changed_by INTEGER REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Real-time Configuration Cache
CREATE TABLE IF NOT EXISTS config_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_platform_configs_platform ON platform_configs(platform);
CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON feature_flags(feature_key);
CREATE INDEX IF NOT EXISTS idx_feature_flags_category ON feature_flags(category);
CREATE INDEX IF NOT EXISTS idx_api_configs_service ON api_configs(service_name);
CREATE INDEX IF NOT EXISTS idx_api_configs_category ON api_configs(category);
CREATE INDEX IF NOT EXISTS idx_admin_activities_admin ON admin_activities(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_activities_created ON admin_activities(created_at);
CREATE INDEX IF NOT EXISTS idx_config_history_type ON config_history(config_type, config_id);
CREATE INDEX IF NOT EXISTS idx_config_cache_key ON config_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_config_cache_expires ON config_cache(expires_at);

-- Insert default platform configurations
INSERT INTO platform_configs (platform, is_enabled, icon, display_name, api_endpoint) VALUES
('instagram', true, '📷', 'Instagram', 'https://graph.instagram.com/v12.0'),
('snapchat', true, '👻', 'Snapchat', 'https://adsapi.snapchat.com/v1'),
('tiktok', false, '🎵', 'TikTok', 'https://open-api.tiktok.com'),
('twitter', false, '🐦', 'Twitter/X', 'https://api.twitter.com/2'),
('facebook', false, '📘', 'Facebook', 'https://graph.facebook.com/v12.0'),
('whatsapp', false, '💬', 'WhatsApp Business', 'https://graph.facebook.com/v12.0'),
('youtube', false, '📺', 'YouTube', 'https://www.googleapis.com/youtube/v3'),
('linkedin', false, '💼', 'LinkedIn', 'https://api.linkedin.com/v2')
ON CONFLICT (platform) DO NOTHING;

-- Insert default feature flags
INSERT INTO feature_flags (feature_key, category, display_name, description, icon) VALUES
('dashboard', 'core', 'Dashboard', 'Main dashboard with analytics overview', '📊'),
('content_studio', 'content', 'Content Studio', 'Upload, edit, and enhance content', '📸'),
('ai_services', 'ai', 'AI Services', 'AI-powered content generation', '🤖'),
('analytics', 'analytics', 'Analytics', 'Performance tracking and insights', '📊'),
('scheduler', 'scheduling', 'Smart Scheduler', 'Automated posting and scheduling', '📅'),
('hygiene_ai', 'compliance', 'Hygiene AI', 'Content moderation and compliance', '🛡️'),
('competitors', 'intelligence', 'Competitor Intelligence', 'Track and analyze competitors', '🏆'),
('accounts', 'management', 'My Accounts', 'Social media account connections', '🔗'),
('content_options', 'content', 'Content Options', 'Content preferences and templates', '🎛️'),
('reports', 'analytics', 'Reports', 'Automated reporting and insights', '📊'),
('settings', 'system', 'Settings', 'Platform settings and preferences', '⚙️'),
('team_management', 'management', 'Team Management', 'Multi-user access and permissions', '👥')
ON CONFLICT (feature_key) DO NOTHING;

-- Insert default packages
INSERT INTO packages (name, display_name, description, price_kwd, features, limits) VALUES
('starter', 'Starter', 'Basic features for small businesses', 19.00, 
 '{"platforms": ["instagram"], "ai_features": ["basic"], "analytics": ["basic"]}',
 '{"posts_per_month": 30, "accounts": 1}'),
('professional', 'Professional', 'Most popular choice', 29.00,
 '{"platforms": ["all"], "ai_features": ["advanced"], "analytics": ["advanced"]}',
 '{"posts_per_month": -1, "accounts": 3}'),
('enterprise', 'Enterprise', 'For restaurant chains', 49.00,
 '{"platforms": ["all"], "ai_features": ["all"], "analytics": ["all"], "api_access": true}',
 '{"posts_per_month": -1, "accounts": -1}')
ON CONFLICT (name) DO NOTHING;

-- Add update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_platform_configs_updated_at BEFORE UPDATE ON platform_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_configs_updated_at BEFORE UPDATE ON api_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_config_cache_updated_at BEFORE UPDATE ON config_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();