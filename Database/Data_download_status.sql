/****** Script for SelectTopNRows command from SSMS  ******/

SELECT 'Total' AS ladder,
	   COUNT(DISTINCT Match_ID) AS MATCH_CNT,
	   COUNT(*) AS ROW_CNT,
	   MIN(convert_match_date) AS MIN_DATE,
	   MAX(convert_match_date) AS MAX_DATE
FROM (SELECT A.*,
			 CASE WHEN CHARINDEX('/',Match_date) <> 0 
				THEN CAST((CAST(CAST(LEFT(Match_date,(CHARINDEX('/',Match_date)-1)) AS INT) AS VARCHAR) +
						'-' + CAST(CAST(REPLACE(SUBSTRING(Match_date,CHARINDEX('/',Match_date)+1,LEN(Match_date)-7),'/','') AS INT) AS VARCHAR) +
						'-' + RIGHT(Match_date,4)) AS DATE) 
				ELSE NULL END AS convert_match_date
	  FROM [AOE2_VOOBLY].[dbo].[RAW_MATCH_DATA] A) M

UNION

SELECT ladder,
	   COUNT(DISTINCT Match_ID) AS MATCH_CNT,
	   COUNT(*) AS ROW_CNT,
	   MIN(convert_match_date) AS MIN_DATE,
	   MAX(convert_match_date) AS MAX_DATE
FROM (SELECT A.*,
			 CASE WHEN CHARINDEX('/',Match_date) <> 0 
				THEN CAST((CAST(CAST(LEFT(Match_date,(CHARINDEX('/',Match_date)-1)) AS INT) AS VARCHAR) +
						'-' + CAST(CAST(REPLACE(SUBSTRING(Match_date,CHARINDEX('/',Match_date)+1,LEN(Match_date)-7),'/','') AS INT) AS VARCHAR) +
						'-' + RIGHT(Match_date,4)) AS DATE) 
				ELSE NULL END AS convert_match_date
	  FROM [AOE2_VOOBLY].[dbo].[RAW_MATCH_DATA] A) M
GROUP BY ladder
ORDER BY 2 DESC
