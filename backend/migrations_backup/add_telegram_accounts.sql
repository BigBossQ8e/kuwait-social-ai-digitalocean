-- Add TelegramAccount table for Kuwait Social AI
-- This migration adds support for Telegram bot integration

-- Create the telegram_accounts table
CREATE TABLE IF NOT EXISTS telegram_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Telegram specific fields
    telegram_id VARCHAR(50) NOT NULL UNIQUE,
    telegram_username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Bot interaction fields
    is_bot_active BOOLEAN DEFAULT TRUE,
    language_preference VARCHAR(10) DEFAULT 'en',
    
    -- Notification preferences
    notify_posts BOOLEAN DEFAULT TRUE,
    notify_analytics BOOLEAN DEFAULT TRUE,
    notify_alerts BOOLEAN DEFAULT TRUE,
    
    -- Verification and security
    verification_code VARCHAR(20),
    verification_expires TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_telegram_accounts_user_id ON telegram_accounts(user_id);
CREATE UNIQUE INDEX idx_telegram_accounts_telegram_id ON telegram_accounts(telegram_id);

-- Create a trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_telegram_accounts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER telegram_accounts_updated_at_trigger
BEFORE UPDATE ON telegram_accounts
FOR EACH ROW
EXECUTE FUNCTION update_telegram_accounts_updated_at();

-- Add a comment to the table
COMMENT ON TABLE telegram_accounts IS 'Stores Telegram account connections for users to receive notifications and interact with the bot';