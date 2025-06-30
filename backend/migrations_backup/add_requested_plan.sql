-- Migration: Add requested_plan to clients table
-- Description: Store the plan that clients request during signup

-- Add requested_plan column to clients table
ALTER TABLE clients 
ADD COLUMN requested_plan VARCHAR(50) DEFAULT 'professional';

-- Update existing pending clients to have professional as default
UPDATE clients 
SET requested_plan = 'professional' 
WHERE subscription_status = 'pending_approval' 
AND requested_plan IS NULL;

-- Add comment for documentation
COMMENT ON COLUMN clients.requested_plan IS 'The subscription plan requested by the client during signup, before admin approval';