-- Migration to fix activity_log table schema
-- Add missing user_agent column and fix any sequence issues

-- Add the missing user_agent column
ALTER TABLE activity_log ADD COLUMN IF NOT EXISTS user_agent VARCHAR(500);

-- Reset the sequence to match the current max ID
SELECT setval('activity_log_id_seq', (SELECT COALESCE(MAX(id), 0) FROM activity_log));

-- Verify the changes
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'activity_log'
ORDER BY ordinal_position;

-- Check sequence is properly set
SELECT currval('activity_log_id_seq') as current_sequence_value;
