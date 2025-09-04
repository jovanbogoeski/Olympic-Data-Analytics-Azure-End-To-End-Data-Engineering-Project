USE OlympicLake;
GO

-- ===== Base views only (no extra analytics) =====

-- Athletes
IF OBJECT_ID(N'dbo.vw_Athletes', N'V') IS NOT NULL DROP VIEW dbo.vw_Athletes;
GO
CREATE VIEW dbo.vw_Athletes AS
SELECT *
FROM OPENROWSET(
  BULK 'transformed-data/athletes/',
  DATA_SOURCE = 'OlympicDataLake',
  FORMAT = 'DELTA'
) AS src;
GO

-- Medals
IF OBJECT_ID(N'dbo.vw_Medals', N'V') IS NOT NULL DROP VIEW dbo.vw_Medals;
GO
CREATE VIEW dbo.vw_Medals AS
SELECT *
FROM OPENROWSET(
  BULK 'transformed-data/medals/',
  DATA_SOURCE = 'OlympicDataLake',
  FORMAT = 'DELTA'
) AS src;
GO

-- Coaches
IF OBJECT_ID(N'dbo.vw_Coaches', N'V') IS NOT NULL DROP VIEW dbo.vw_Coaches;
GO
CREATE VIEW dbo.vw_Coaches AS
SELECT *
FROM OPENROWSET(
  BULK 'transformed-data/coaches/',
  DATA_SOURCE = 'OlympicDataLake',
  FORMAT = 'DELTA'
) AS src;
GO

-- EntriesGender
IF OBJECT_ID(N'dbo.vw_EntriesGender', N'V') IS NOT NULL DROP VIEW dbo.vw_EntriesGender;
GO
CREATE VIEW dbo.vw_EntriesGender AS
SELECT *
FROM OPENROWSET(
  BULK 'transformed-data/entriesgender/',
  DATA_SOURCE = 'OlympicDataLake',
  FORMAT = 'DELTA'
) AS src;
GO

-- Teams
IF OBJECT_ID(N'dbo.vw_Teams', N'V') IS NOT NULL DROP VIEW dbo.vw_Teams;
GO
CREATE VIEW dbo.vw_Teams AS
SELECT *
FROM OPENROWSET(
  BULK 'transformed-data/teams/',
  DATA_SOURCE = 'OlympicDataLake',
  FORMAT = 'DELTA'
) AS src;
GO
