-- Add AI Prompts Management Tables for SQLite

-- AI Prompts table
CREATE TABLE IF NOT EXISTS ai_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    parameters TEXT,
    
    -- Kuwaiti NLP Configuration
    enable_kuwaiti_nlp BOOLEAN DEFAULT 1,
    dialect_processing VARCHAR(50) DEFAULT 'auto',
    kuwaiti_context TEXT,
    
    -- Metadata
    name VARCHAR(200) NOT NULL,
    description TEXT,
    tags TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT 1,
    is_default BOOLEAN DEFAULT 0,
    
    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES admins(id)
);

-- AI Prompt Versions table
CREATE TABLE IF NOT EXISTS ai_prompt_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL REFERENCES ai_prompts(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    
    -- Snapshot of prompt at this version
    system_prompt TEXT,
    user_prompt_template TEXT,
    model VARCHAR(50),
    temperature FLOAT,
    max_tokens INTEGER,
    parameters TEXT,
    
    -- Version metadata
    change_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES admins(id)
);

-- AI Prompt Templates table
CREATE TABLE IF NOT EXISTS ai_prompt_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    tags TEXT,
    is_featured BOOLEAN DEFAULT 0,
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ai_prompts_key ON ai_prompts(prompt_key);
CREATE INDEX IF NOT EXISTS idx_ai_prompts_service ON ai_prompts(service);
CREATE INDEX IF NOT EXISTS idx_ai_prompts_category ON ai_prompts(category);
CREATE INDEX IF NOT EXISTS idx_ai_prompts_active ON ai_prompts(is_active);

CREATE INDEX IF NOT EXISTS idx_ai_prompt_versions_prompt ON ai_prompt_versions(prompt_id);
CREATE INDEX IF NOT EXISTS idx_ai_prompt_versions_number ON ai_prompt_versions(prompt_id, version_number);

CREATE INDEX IF NOT EXISTS idx_ai_prompt_templates_category ON ai_prompt_templates(category);
CREATE INDEX IF NOT EXISTS idx_ai_prompt_templates_featured ON ai_prompt_templates(is_featured);

-- Insert default templates
INSERT INTO ai_prompt_templates (name, category, description, system_prompt, user_prompt_template, suggested_model, tags, is_featured) VALUES
(
    'Kuwait Restaurant Post',
    'content',
    'Perfect for restaurant social media posts with Kuwaiti cultural context',
    'You are a social media expert specializing in Kuwaiti food culture. Create engaging posts that resonate with local tastes and traditions.',
    'Create an engaging social media post for a {platform} about {dish_name} at {restaurant_name} in Kuwait. Consider:
- Local taste preferences
- Prayer time considerations
- Seasonal factors (current temp: {temperature}°C)
- Include relevant Kuwaiti expressions
- Add appropriate emojis
- Suggest 5-7 hashtags mixing English and Arabic

Input: {input}',
    'gpt-4',
    '["restaurant", "food", "kuwait", "arabic"]',
    1
);

INSERT INTO ai_prompt_templates (name, category, description, system_prompt, user_prompt_template, suggested_model, tags, is_featured) VALUES
(
    'Retail Promotion Kuwait',
    'content',
    'Generate promotional content for retail businesses in Kuwait',
    'You are a marketing expert familiar with Kuwaiti shopping culture and consumer behavior.',
    'Create a promotional post for {business_name} offering {promotion_type}. Consider:
- Kuwait shopping habits
- Local holidays and events
- Weather considerations
- Family-oriented messaging
- Mix of Arabic and English

Promotion details: {input}',
    'gpt-4',
    '["retail", "promotion", "kuwait", "shopping"]',
    1
);

INSERT INTO ai_prompt_templates (name, category, description, system_prompt, user_prompt_template, suggested_model, tags, is_featured) VALUES
(
    'Engagement Analysis Kuwait',
    'analysis',
    'Analyze social media engagement for Kuwaiti audience',
    'You are a social media analyst specializing in Gulf region consumer behavior.',
    'Analyze the engagement patterns for {business_type} in Kuwait based on:
{input}

Provide insights on:
- Best posting times considering prayer schedules
- Content themes that resonate
- Language preferences (Arabic vs English)
- Seasonal trends
- Competitor comparison',
    'gpt-4',
    '["analytics", "engagement", "kuwait"]',
    0
);