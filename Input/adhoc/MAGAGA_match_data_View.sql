/****** Script for SelectTopNRows command from SSMS  ******/

CREATE VIEW [magaga].[MATCH_DATA] AS
SELECT M.MATCH_ID
	  ,B.map_name AS MAP
	  ,PLAYER	  
	  ,C.name AS PLAYER_NAME
	  ,C.winner AS WIN
	  ,C.civilization AS CIV
      ,INSTANCE_ID
	  ,CREATE_TIME
	  ,DESTROY_TIME
      ,TIME_STAMP
      ,INSTANCE
	  ,TYPE
	  ,D.food AS FOOD
	  ,D.wood AS WOOD
	  ,D.gold AS GOLD
	  ,D.stone AS STONE
FROM (SELECT A.[match_id] AS MATCH_ID
			,A.player_number AS PLAYER
			,A.[instance_id] AS INSTANCE_ID
			,CAST(created AS TIME(0)) AS CREATE_TIME
			,CAST(destroyed AS TIME(0)) AS DESTROY_TIME
			,CAST(A.timestamp AS TIME(0)) AS TIME_STAMP
			,A.[name] AS INSTANCE
			,'Interaction' AS TYPE
		FROM [AOE2_VOOBLY].[magaga].[STATES] A
		LEFT JOIN [AOE2_VOOBLY].[magaga].[INSTANCES] C ON A.match_id = C.match_id AND A.instance_id = C.instance_id

	  UNION

	  SELECT A.[match_id] AS MATCH_ID
		    ,[player_number] AS PLAYER
		    ,[technology_id] AS INSTANCE_ID
		    ,CAST(started AS TIME(0)) CREATE_TIME
		    ,'00:00:00' AS DESTROY_TIME
		    ,CAST(started AS TIME(0)) TIME_STAMP
		    ,[name] AS INSTANCE
		    ,'Research' AS TYPE
	  FROM [AOE2_VOOBLY].[magaga].[RESEARCH] A) M
LEFT JOIN [AOE2_VOOBLY].[magaga].[MATCHES] B ON M.match_id = B.id
LEFT JOIN [AOE2_VOOBLY].[magaga].[PLAYERS] C ON M.MATCH_ID = C.match_id AND M.PLAYER = C.number
LEFT JOIN [AOE2_VOOBLY].[magaga].[RESOURCES] D ON M.match_id = D.match_id AND M.PLAYER = D.player_number AND CAST(M.TIME_STAMP AS TIME(0)) = CAST(D.timestamp AS TIME(0))
WHERE PLAYER <> 0

