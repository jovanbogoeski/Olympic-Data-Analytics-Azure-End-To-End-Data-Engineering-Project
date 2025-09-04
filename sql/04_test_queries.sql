USE OlympicLake;
GO

/* ===========================
   04_test_queries.sql
   Quick smoke tests + simple insights
   =========================== */

-- 1) Confirm views exist
SELECT name
FROM sys.views
WHERE name IN ('vw_Athletes','vw_Medals','vw_Coaches','vw_EntriesGender','vw_Teams')
ORDER BY name;
GO

-- 2) Row counts per view (sanity check)
SELECT 'vw_Athletes'      AS view_name, COUNT_BIG(*) AS row_count FROM dbo.vw_Athletes
UNION ALL SELECT 'vw_Medals',        COUNT_BIG(*) FROM dbo.vw_Medals
UNION ALL SELECT 'vw_Coaches',       COUNT_BIG(*) FROM dbo.vw_Coaches
UNION ALL SELECT 'vw_EntriesGender', COUNT_BIG(*) FROM dbo.vw_EntriesGender
UNION ALL SELECT 'vw_Teams',         COUNT_BIG(*) FROM dbo.vw_Teams;
GO

-- 3) Sample rows
SELECT TOP 10 * FROM dbo.vw_Athletes;       GO
SELECT TOP 10 * FROM dbo.vw_Medals;         GO
SELECT TOP 10 * FROM dbo.vw_Coaches;        GO
SELECT TOP 10 * FROM dbo.vw_EntriesGender;  GO
SELECT TOP 10 * FROM dbo.vw_Teams;          GO

/* ---------- Medals (country aggregates) ---------- */

-- 4) Medal tallies by country
SELECT
  TeamCountry,
  SUM(TRY_CAST(Gold   AS BIGINT))  AS Gold,
  SUM(TRY_CAST(Silver AS BIGINT))  AS Silver,
  SUM(TRY_CAST(Bronze AS BIGINT))  AS Bronze,
  SUM(TRY_CAST(Total  AS BIGINT))  AS TotalMedals
FROM dbo.vw_Medals
GROUP BY TeamCountry
ORDER BY TotalMedals DESC, Gold DESC, Silver DESC, Bronze DESC;
GO

-- 5) Medal points ranking (uses your medal_points column)
SELECT
  TeamCountry,
  SUM(TRY_CAST(medal_points AS BIGINT)) AS MedalPoints
FROM dbo.vw_Medals
GROUP BY TeamCountry
ORDER BY MedalPoints DESC;
GO

/* ---------- Athletes / Coaches / Teams ---------- */

-- 6) Athletes by country
SELECT Country, COUNT(*) AS AthleteCount
FROM dbo.vw_Athletes
GROUP BY Country
ORDER BY AthleteCount DESC;
GO

-- 7) Athletes by discipline
SELECT Discipline, COUNT(*) AS AthleteCount
FROM dbo.vw_Athletes
GROUP BY Discipline
ORDER BY AthleteCount DESC;
GO

-- 8) Coaches by discipline and country
SELECT Discipline, Country, COUNT(*) AS CoachCount
FROM dbo.vw_Coaches
GROUP BY Discipline, Country
ORDER BY CoachCount DESC;
GO

-- 9) Teams per discipline
SELECT Discipline, COUNT(DISTINCT TeamName) AS TeamsCount
FROM dbo.vw_Teams
GROUP BY Discipline
ORDER BY TeamsCount DESC;
GO

/* ---------- Gender (EntriesGender) ---------- */

-- 10) Gender distribution by discipline (compute % safely)
SELECT
  Discipline,
  SUM(TRY_CAST(Female AS BIGINT)) AS Female,
  SUM(TRY_CAST(Male   AS BIGINT)) AS Male,
  SUM(TRY_CAST(Total  AS BIGINT)) AS Total,
  CASE WHEN SUM(TRY_CAST(Total AS BIGINT)) > 0
       THEN 1.0 * SUM(TRY_CAST(Female AS BIGINT)) / SUM(TRY_CAST(Total AS BIGINT))
       ELSE NULL END AS FemalePct,
  CASE WHEN SUM(TRY_CAST(Total AS BIGINT)) > 0
       THEN 1.0 * SUM(TRY_CAST(Male AS BIGINT)) / SUM(TRY_CAST(Total AS BIGINT))
       ELSE NULL END AS MalePct
FROM dbo.vw_EntriesGender
GROUP BY Discipline
ORDER BY Total DESC;
GO

/* ---------- Freshness ---------- */

-- 11) Ingestion windows per view (min/max)
SELECT 'vw_Athletes' AS view_name,
       MIN(ingestion_date) AS min_ingestion_date, MAX(ingestion_date) AS max_ingestion_date FROM dbo.vw_Athletes
UNION ALL
SELECT 'vw_Medals', MIN(ingestion_date), MAX(ingestion_date) FROM dbo.vw_Medals
UNION ALL
SELECT 'vw_Coaches', MIN(ingestion_date), MAX(ingestion_date) FROM dbo.vw_Coaches
UNION ALL
SELECT 'vw_EntriesGender', MIN(ingestion_date), MAX(ingestion_date) FROM dbo.vw_EntriesGender
UNION ALL
SELECT 'vw_Teams', MIN(ingestion_date), MAX(ingestion_date) FROM dbo.vw_Teams;
GO
