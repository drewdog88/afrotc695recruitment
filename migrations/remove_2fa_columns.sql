-- Migration to remove 2FA columns from user table
-- This migration removes all two-factor authentication related columns

-- Remove 2FA columns from user table
ALTER TABLE "user" DROP COLUMN IF EXISTS totp_secret;
ALTER TABLE "user" DROP COLUMN IF EXISTS totp_enabled;
ALTER TABLE "user" DROP COLUMN IF EXISTS backup_codes_hash;
ALTER TABLE "user" DROP COLUMN IF EXISTS totp_setup_completed;
ALTER TABLE "user" DROP COLUMN IF EXISTS can_enable_2fa;
