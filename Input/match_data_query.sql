SELECT TOP 100000 *
FROM [AOE2_VOOBLY].[dbo].[MATCH_DATA]
WHERE ladder = 'Ladder: RM - 1v1' AND
	  Match_map IN (SELECT Match_map
					FROM [AOE2_VOOBLY].[dbo].[MATCH_DATA]
					WHERE ladder = 'Ladder: RM - 1v1'
					GROUP BY Match_map
					HAVING COUNT(*) > 100) AND
	  Match_mod IN (SELECT Match_mod
					FROM [AOE2_VOOBLY].[dbo].[MATCH_DATA]
					WHERE ladder = 'Ladder: RM - 1v1'
					GROUP BY Match_mod
					HAVING COUNT(*) > 1000) AND
	  Match_length > 5 