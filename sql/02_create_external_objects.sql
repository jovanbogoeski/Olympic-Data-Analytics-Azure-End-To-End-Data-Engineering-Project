USE OlympicLake;
GO

-- Create a database scoped credential using the Synapse Managed Identity
-- This requires that the Synapse workspace Managed Identity has
-- "Storage Blob Data Reader" role on the storage account.
IF NOT EXISTS (
    SELECT * FROM sys.database_scoped_credentials WHERE name = 'SynapseManagedIdentity'
)
CREATE DATABASE SCOPED CREDENTIAL SynapseManagedIdentity
WITH IDENTITY = 'Managed Identity';
GO

-- Create an external data source pointing to the ADLS Gen2 container
-- Update LOCATION if your container or account name changes
IF NOT EXISTS (
    SELECT * FROM sys.external_data_sources WHERE name = 'OlympicDataLake'
)
CREATE EXTERNAL DATA SOURCE OlympicDataLake
WITH (
    LOCATION   = 'abfss://tokyo-olumpic-data@tokyoolympicdatajovan.dfs.core.windows.net',
    CREDENTIAL = SynapseManagedIdentity
);
GO
