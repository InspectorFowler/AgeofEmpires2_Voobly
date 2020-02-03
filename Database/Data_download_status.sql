/****** Script for SelectTopNRows command from SSMS  ******/

SELECT 'Total' AS ladder,
	   COUNT(DISTINCT Match_ID) AS MATCH_CNT,
	   COUNT(*) AS ROW_CNT
FROM [AOE2_VOOBLY].[dbo].[RAW_MATCH_DATA]r

UNION

SELECT ladder, 
	   COUNT(DISTINCT Match_ID) AS MATCH_CNT,
	   COUNT(*) AS ROW_CNT
FROM [AOE2_VOOBLY].[dbo].[RAW_MATCH_DATA]
GROUP BY ladder
ORDER BY 2 DESC