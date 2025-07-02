-- Fix All Database Schema Issues
-- This migration updates all tables to match the current model definitions

-- 1. Fix telegram_accounts table
ALTER TABLE telegram_accounts 
ADD COLUMN IF NOT EXISTS client_id INTEGER REFERENCES clients(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS chat_id VARCHAR(100) UNIQUE,
ADD COLUMN IF NOT EXISTS bot_token VARCHAR(200),
ADD COLUMN IF NOT EXISTS bot_username VARCHAR(100),
ADD COLUMN IF NOT EXISTS bot_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS webhook_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS notify_approvals BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create index for client_id
CREATE INDEX IF NOT EXISTS idx_telegram_accounts_client_id ON telegram_accounts(client_id);

-- 2. Create post_approvals table if it doesn't exist
CREATE TABLE IF NOT EXISTS post_approvals (
    id SERIAL PRIMARY KEY,
    telegram_account_id INTEGER NOT NULL REFERENCES telegram_accounts(id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    message_id VARCHAR(100),
    chat_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    response_text TEXT,
    approval_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for post_approvals
CREATE INDEX IF NOT EXISTS idx_post_approvals_telegram_account_id ON post_approvals(telegram_account_id);
CREATE INDEX IF NOT EXISTS idx_post_approvals_post_id ON post_approvals(post_id);
CREATE INDEX IF NOT EXISTS idx_post_approvals_status ON post_approvals(status);

-- 3. Create telegram_commands table if it doesn't exist
CREATE TABLE IF NOT EXISTS telegram_commands (
    id SERIAL PRIMARY KEY,
    telegram_account_id INTEGER NOT NULL REFERENCES telegram_accounts(id) ON DELETE CASCADE,
    command VARCHAR(50) NOT NULL,
    parameters JSON,
    response_sent TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- Create index for telegram_commands
CREATE INDEX IF NOT EXISTS idx_telegram_commands_telegram_account_id ON telegram_commands(telegram_account_id);
CREATE INDEX IF NOT EXISTS idx_telegram_commands_command ON telegram_commands(command);

-- 4. Create config_syncs table (from admin panel)
CREATE TABLE IF NOT EXISTS config_syncs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    sync_version VARCHAR(50),
    config_hash VARCHAR(64),
    synced_data JSON,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_status VARCHAR(20) DEFAULT 'success',
    error_message TEXT
);

-- Create indexes for config_syncs
CREATE INDEX IF NOT EXISTS idx_config_sync_client ON config_syncs(client_id);
CREATE INDEX IF NOT EXISTS idx_config_sync_timestamp ON config_syncs(synced_at);
CREATE INDEX IF NOT EXISTS idx_config_sync_status ON config_syncs(sync_status);

-- 5. Add missing columns to other tables if needed
-- Ensure all admin panel tables exist (they should from previous migrations)

-- 6. Update existing telegram_accounts records to have valid chat_id if missing
UPDATE telegram_accounts 
SET chat_id = CONCAT('temp_', id::text) 
WHERE chat_id IS NULL OR chat_id = '';

-- 7. Add comments for documentation
COMMENT ON TABLE post_approvals IS 'Tracks Telegram approval requests for posts';
COMMENT ON TABLE telegram_commands IS 'Logs Telegram bot commands executed by users';
COMMENT ON COLUMN telegram_accounts.client_id IS 'Link to client account for multi-tenant support';
COMMENT ON COLUMN telegram_accounts.chat_id IS 'Unique Telegram chat identifier';

-- 8. Grant necessary permissions (adjust based on your database user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- Migration complete
-- This fixes all schema issues and makes the database match the model definitions