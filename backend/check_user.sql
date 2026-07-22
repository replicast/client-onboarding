-- Check if user 'steve' exists in client_onboarding database
-- Run this in client_onboarding database

SELECT
    name,
    type_desc,
    authentication_type_desc,
    create_date
FROM sys.database_principals
WHERE name = 'steve';

-- Also check if there's a server-level login
-- Note: This query will fail if you don't have permissions to query master
-- That's okay, just run it to see
SELECT name, type_desc, create_date
FROM sys.server_principals
WHERE name = 'steve';
