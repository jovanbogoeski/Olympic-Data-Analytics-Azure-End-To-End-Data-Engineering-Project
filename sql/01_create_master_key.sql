USE OlympicLake;
GO

-- Create a Master Key in the database
-- This is required before creating any database scoped credentials
-- Replace the password with a strong one (min 8 chars, mix of upper/lower/numbers/symbols)
-- NOTE: You only need to run this once per database

IF NOT EXISTS (
    SELECT * FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##'
)
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'YourStrongPassword123!';
GO
