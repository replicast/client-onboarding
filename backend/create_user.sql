-- Create SQL User in Azure SQL Database
-- Run this script in Azure Portal Query Editor for the 'client_onboarding' database

-- IMPORTANT: Connect to the 'client_onboarding' DATABASE (not master) before running this

-- Create login at server level (run in master database)
-- You need to run this part in the 'master' database first
-- CREATE LOGIN steve WITH PASSWORD = 'Grundig7';

-- Create user in the client_onboarding database
-- Run this in the 'client_onboarding' database
CREATE USER steve FOR LOGIN steve;

-- Grant permissions to the user
ALTER ROLE db_owner ADD MEMBER steve;

-- Verify user was created
SELECT name, type_desc, create_date
FROM sys.database_principals
WHERE name = 'steve';
