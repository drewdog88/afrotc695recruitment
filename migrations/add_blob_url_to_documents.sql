-- Add blob_url field to recruitment_document table
-- This will store the Vercel Blob storage URL for documents

ALTER TABLE recruitment_document
ADD COLUMN blob_url VARCHAR(500);

-- Add a comment to document the purpose
COMMENT ON COLUMN recruitment_document.blob_url IS 'Vercel Blob storage URL for the document file';
