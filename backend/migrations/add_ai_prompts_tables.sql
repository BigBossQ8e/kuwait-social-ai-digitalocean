-- Add AI Prompts Management Tables

-- AI Prompts table
CREATE TABLE IF NOT EXISTS ai_prompts (
    id SERIAL PRIMARY KEY,
    prompt_key VARCHAR(100) UNIQUE NOT NULL,
    service VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    
    -- Prompt content
    system_prompt TEXT,
    user_prompt_template TEXT NOT NULL,
    
    -- Configuration
    model VARCHAR(50),
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 500,
    parameters JSON,
    
    -- Kuwaiti NLP Configuration
    enable_kuwaiti_nlp BOOLEAN DEFAULT TRUE,
    dialect_processing VARCHAR(50) DEFAULT 'auto',
    kuwaiti_context JSON,
    
    -- Metadata
    name VARCHAR(200) NOT NULL,
    description TEXT,
    tags JSON,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    
    -- Tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES admins(id),
    
    -- Indexes
    INDEX idx_ai_prompts_key (prompt_key),
    INDEX idx_ai_prompts_service (service),
    INDEX idx_ai_prompts_category (category),
    INDEX idx_ai_prompts_active (is_active)
);

-- AI Prompt Versions table
CREATE TABLE IF NOT EXISTS ai_prompt_versions (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER NOT NULL REFERENCES ai_prompts(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    
    -- Snapshot of prompt at this version
    system_prompt TEXT,
    user_prompt_template TEXT,
    model VARCHAR(50),
    temperature FLOAT,
    max_tokens INTEGER,
    parameters JSON,
    
    -- Version metadata
    change_note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES admins(id),
    
    -- Indexes
    INDEX idx_ai_prompt_versions_prompt (prompt_id),
    INDEX idx_ai_prompt_versions_number (prompt_id, version_number)
);

-- AI Prompt Templates table
CREATE TABLE IF NOT EXISTS ai_prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    
    -- Template content
    system_prompt TEXT,
    user_prompt_template TEXT NOT NULL,
    
    -- Suggested configuration
    suggested_model VARCHAR(50),
    suggested_temperature FLOAT DEFAULT 0.7,
    suggested_max_tokens INTEGER DEFAULT 500,
    
    -- Example usage
    example_input TEXT,
    example_output TEXT,
    
    -- Metadata
    tags JSON,
    is_featured BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_ai_prompt_templates_category (category),
    INDEX idx_ai_prompt_templates_featured (is_featured)
);

-- Insert default templates
INSERT INTO ai_prompt_templates (name, category, description, system_prompt, user_prompt_template, suggested_model, tags, is_featured) VALUES
(
    'Kuwait Restaurant Post',
    'content',
    'Perfect for restaurant social media posts with Kuwaiti cultural context',
    'You are a social media expert specializing in Kuwaiti food culture. Create engaging posts that resonate with local tastes and traditions.',
    'Create an engaging social media post for a {platform} about {dish_name} at {restaurant_name} in Kuwait. Consider:\n- Local taste preferences\n- Prayer time considerations\n- Seasonal factors (current temp: {temperature}°C)\n- Include relevant Kuwaiti expressions\n- Add appropriate emojis\n- Suggest 5-7 hashtags mixing English and Arabic\n\nInput: {input}',
    'gpt-4',
    '["restaurant", "food", "kuwait", "arabic"]',
    TRUE
),
(
    'Retail Promotion Kuwait',
    'content',
    'Generate promotional content for retail businesses in Kuwait',
    'You are a marketing expert familiar with Kuwaiti shopping culture and consumer behavior.',
    'Create a promotional post for {business_name} offering {promotion_type}. Consider:\n- Kuwait shopping habits\n- Local holidays and events\n- Weather considerations\n- Family-oriented messaging\n- Mix of Arabic and English\n\nPromotion details: {input}',
    'gpt-4',
    '["retail", "promotion", "kuwait", "shopping"]',
    TRUE
),
(
    'Engagement Analysis Kuwait',
    'analysis',
    'Analyze social media engagement for Kuwaiti audience',
    'You are a social media analyst specializing in Gulf region consumer behavior.',
    'Analyze the engagement patterns for {business_type} in Kuwait based on:\n{input}\n\nProvide insights on:\n- Best posting times considering prayer schedules\n- Content themes that resonate\n- Language preferences (Arabic vs English)\n- Seasonal trends\n- Competitor comparison',
    'gpt-4',
    '["analytics", "engagement", "kuwait"]',
    FALSE
);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ai_prompts_updated_at BEFORE UPDATE
    ON ai_prompts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();