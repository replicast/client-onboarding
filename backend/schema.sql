-- Client Onboarding Database Schema
-- Run this script in Azure SQL Database to create the tables

-- Create clients table
CREATE TABLE clients (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    country NVARCHAR(100) NOT NULL,
    business_type NVARCHAR(100) NOT NULL,
    organization_size NVARCHAR(50) NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE(),
    created_by NVARCHAR(255)
);

-- Create indexes on clients table
CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_country ON clients(country);

-- Create sites table
CREATE TABLE sites (
    id INT IDENTITY(1,1) PRIMARY KEY,
    client_id INT NOT NULL,
    name NVARCHAR(255) NOT NULL,
    site_type NVARCHAR(100) NOT NULL,
    -- GeoJSON polygon stored as text (GEOGRAPHY is incompatible with pymssql/Azure SQL)
    geolocation_polygon NVARCHAR(MAX) NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE(),
    created_by NVARCHAR(255),
    CONSTRAINT fk_sites_client FOREIGN KEY (client_id)
        REFERENCES clients(id) ON DELETE CASCADE
);

-- Create index on sites table
CREATE INDEX idx_sites_client_id ON sites(client_id);

-- Create documents table
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
    CONSTRAINT fk_documents_client FOREIGN KEY (client_id)
        REFERENCES clients(id) ON DELETE CASCADE
);

-- Create index on documents table
CREATE INDEX idx_document_client_id ON documents(client_id);

-- Verify tables were created
SELECT
    TABLE_NAME,
    TABLE_TYPE
FROM
    INFORMATION_SCHEMA.TABLES
WHERE
    TABLE_NAME IN ('clients', 'sites', 'documents')
ORDER BY
    TABLE_NAME;
