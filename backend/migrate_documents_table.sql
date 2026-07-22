-- Migration: Create documents table for PDF document storage
-- Run this script against your Azure SQL Database

-- Create documents table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='documents' AND xtype='U')
BEGIN
    CREATE TABLE documents (
        id INT IDENTITY(1,1) PRIMARY KEY,
        client_id INT NOT NULL,
        filename NVARCHAR(255) NOT NULL,
        original_filename NVARCHAR(255) NOT NULL,
        content_type NVARCHAR(100) DEFAULT 'application/pdf',
        file_size BIGINT NOT NULL,
        blob_name NVARCHAR(500) NOT NULL,
        created_at DATETIME2 DEFAULT GETUTCDATE(),
        uploaded_by NVARCHAR(255) NULL,
        CONSTRAINT FK_documents_client FOREIGN KEY (client_id)
            REFERENCES clients(id) ON DELETE CASCADE
    );

    -- Create index on client_id for faster lookups
    CREATE INDEX idx_document_client_id ON documents(client_id);

    PRINT 'Documents table created successfully';
END
ELSE
BEGIN
    PRINT 'Documents table already exists';
END
GO
