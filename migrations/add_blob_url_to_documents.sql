-- Migration: Add blob_url column to recruitment_document table
-- Description: Adds blob_url column to store Vercel Blob storage URLs for documents
-- Database: PostgreSQL (Neon)
-- Date: 2025-08-17
-- Author: AFROTC 695 Recruitment System

-- Add blob_url column to recruitment_document table
ALTER TABLE "recruitment_document" ADD COLUMN IF NOT EXISTS blob_url VARCHAR(500);

-- Add comment for documentation
COMMENT ON COLUMN "recruitment_document".blob_url IS 'Vercel Blob storage URL for the document file';

-- Verify the migration
DO $$
BEGIN
    -- Check if column was added successfully
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'recruitment_document'
        AND column_name = 'blob_url'
    ) THEN
        RAISE EXCEPTION 'Migration failed: blob_url column not found';
    END IF;

    RAISE NOTICE 'Migration completed successfully: blob_url column added to recruitment_document table';
END $$;
