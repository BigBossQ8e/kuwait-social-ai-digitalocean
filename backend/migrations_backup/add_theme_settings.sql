-- Migration: Add theme settings tables
-- Description: Tables for storing dynamic theme and branding configuration

-- Theme settings table for individual settings
CREATE TABLE IF NOT EXISTS theme_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) NOT NULL DEFAULT 'text',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);

-- Theme presets for complete theme configurations
CREATE TABLE IF NOT EXISTS theme_presets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    settings JSONB NOT NULL,
    screenshot_url VARCHAR(500),
    is_active BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);

-- Theme change history for tracking changes
CREATE TABLE IF NOT EXISTS theme_history (
    id SERIAL PRIMARY KEY,
    preset_id INTEGER REFERENCES theme_presets(id),
    settings_snapshot JSONB NOT NULL,
    changed_by INTEGER REFERENCES users(id),
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default theme settings
INSERT INTO theme_settings (setting_key, setting_value, setting_type, description) VALUES
-- Branding
('site_name', 'Kuwait Social AI', 'text', 'Main site name'),
('site_tagline', 'AI-Powered Social Media for Kuwait F&B', 'text', 'Site tagline'),
('logo_url', '/assets/logo.png', 'image', 'Site logo URL'),
('favicon_url', '/favicon.ico', 'image', 'Favicon URL'),

-- Colors
('primary_color', '#007bff', 'color', 'Primary brand color'),
('secondary_color', '#764ba2', 'color', 'Secondary brand color'),
('gradient_start', '#667eea', 'color', 'Hero gradient start color'),
('gradient_end', '#764ba2', 'color', 'Hero gradient end color'),
('text_color', '#333333', 'color', 'Main text color'),
('bg_color', '#ffffff', 'color', 'Background color'),

-- Typography
('primary_font', 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 'font', 'Primary font family'),
('heading_font', 'inherit', 'font', 'Heading font family'),
('font_size_base', '16px', 'text', 'Base font size'),

-- Hero Section
('hero_title', 'AI-Powered Social Media for Kuwait F&B 🍽️', 'text', 'Hero section title'),
('hero_subtitle', 'Create mouth-watering content for restaurants & cafes in Arabic & English instantly', 'text', 'Hero section subtitle'),
('hero_cta_primary', 'Start Free Trial', 'text', 'Primary CTA button text'),
('hero_cta_secondary', 'Learn More', 'text', 'Secondary CTA button text'),
('hero_style', 'gradient', 'select', 'Hero section style: gradient, image, video'),
('hero_bg_image', '', 'image', 'Hero background image URL'),

-- Features Section
('features_enabled', 'true', 'boolean', 'Show features section'),
('features_title', 'Built for Kuwait''s Food & Beverage Industry', 'text', 'Features section title'),

-- Pricing Section
('pricing_enabled', 'true', 'boolean', 'Show pricing section'),
('pricing_title', 'Simple, Transparent Pricing', 'text', 'Pricing section title'),
('currency_symbol', 'KWD', 'text', 'Currency symbol'),

-- Layout Options
('show_header', 'true', 'boolean', 'Show header navigation'),
('show_footer', 'true', 'boolean', 'Show footer'),
('enable_rtl', 'false', 'boolean', 'Enable RTL layout for Arabic'),

-- Custom CSS
('custom_css', '', 'css', 'Custom CSS overrides');

-- Insert default theme preset
INSERT INTO theme_presets (name, description, settings, is_active, is_default) VALUES (
    'Default Theme',
    'Kuwait Social AI default branding',
    '{
        "site_name": "Kuwait Social AI",
        "primary_color": "#007bff",
        "secondary_color": "#764ba2",
        "gradient_start": "#667eea",
        "gradient_end": "#764ba2",
        "hero_style": "gradient",
        "features_enabled": true,
        "pricing_enabled": true
    }'::jsonb,
    true,
    true
);

-- Create indexes for performance
CREATE INDEX idx_theme_settings_key ON theme_settings(setting_key);
CREATE INDEX idx_theme_presets_active ON theme_presets(is_active);
CREATE INDEX idx_theme_history_created ON theme_history(created_at DESC);

-- Create update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_theme_settings_updated_at BEFORE UPDATE ON theme_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_theme_presets_updated_at BEFORE UPDATE ON theme_presets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();