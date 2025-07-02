-- Configuration Sync Table
-- Tracks configuration synchronization for clients

CREATE TABLE IF NOT EXISTS config_syncs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    sync_version VARCHAR(50),
    config_hash VARCHAR(64),
    synced_data JSON,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    
    -- Indexes for performance
    CONSTRAINT config_syncs_client_id_idx INDEX (client_id),
    CONSTRAINT config_syncs_timestamp_idx INDEX (synced_at)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_config_sync_client ON config_syncs(client_id);
CREATE INDEX IF NOT EXISTS idx_config_sync_timestamp ON config_syncs(synced_at);
CREATE INDEX IF NOT EXISTS idx_config_sync_status ON config_syncs(sync_status);

-- Add comment
COMMENT ON TABLE config_syncs IS 'Tracks configuration synchronization history for clients';