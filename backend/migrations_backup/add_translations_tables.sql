-- Create translations table
CREATE TABLE IF NOT EXISTS translations (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL,
    locale VARCHAR(10) NOT NULL,
    value TEXT NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    UNIQUE(key, locale)
);

-- Create translation history table
CREATE TABLE IF NOT EXISTS translation_history (
    id SERIAL PRIMARY KEY,
    translation_id INTEGER REFERENCES translations(id) ON DELETE CASCADE,
    old_value TEXT,
    new_value TEXT,
    changed_by INTEGER REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_translations_key ON translations(key);
CREATE INDEX idx_translations_locale ON translations(locale);
CREATE INDEX idx_translations_category ON translations(category);
CREATE INDEX idx_translation_history_translation_id ON translation_history(translation_id);

-- Create trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_translations_updated_at BEFORE UPDATE
    ON translations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial translations from current system
-- This will be populated by a separate script