-- Migration: Convert geolocation_polygon from GEOGRAPHY to TEXT
-- This fixes compatibility with pymssql and Azure SQL Server

-- Step 1: Drop the existing GEOGRAPHY column
ALTER TABLE sites
DROP COLUMN geolocation_polygon;

-- Step 2: Add new TEXT column for storing GeoJSON as text
ALTER TABLE sites
ADD geolocation_polygon NVARCHAR(MAX) NULL;

-- Done! The column is now TEXT (NVARCHAR) instead of GEOGRAPHY
