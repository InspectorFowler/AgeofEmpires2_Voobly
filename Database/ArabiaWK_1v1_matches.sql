/****** Script for SelectTopNRows command from SSMS  ******/
SELECT *
FROM [AOE2_VOOBLY].[dbo].[RAW_MATCH_DATA] A
WHERE A.Match_mod LIKE '%Wololo%' AND
	  ladder = 'Ladder: RM - 1v1' AND
	  Match_map = 'Arabia' AND
	  CAST(Match_rating AS INT) > 1700