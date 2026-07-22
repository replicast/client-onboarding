-- Recreate SQL User in Azure SQL Database
-- Run this in Azure Portal Query Editor for the 'client_onboarding' database

-- First, drop the user if it exists (to start fresh)
-- You might get an error if the user doesn't exist - that's okay
DROP USER IF EXISTS steve;

-- Create a contained database user (doesn't require a login in master)
-- This is the recommended approach for Azure SQL Database
CREATE USER steve WITH PASSWORD = 'Grundig7';

-- Grant db_owner role (full permissions)
ALTER ROLE db_owner ADD MEMBER steve;

-- Verify user was created
SELECT
    name,
    type_desc,
    authentication_type_desc,
    create_date
FROM sys.database_principals
WHERE name = 'steve';
