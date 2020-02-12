/****** Script for SelectTopNRows command from SSMS  ******/
SELECT A.[match_id]
	  ,map_name
      ,A.[instance_id]
	  ,created
	  ,destroyed
      ,[timestamp]
      ,[player_number]
      ,[class_id]
      ,[object_id]
      ,[name]
 FROM [AOE2_VOOBLY].[magaga].[STATES] A
 LEFT JOIN [AOE2_VOOBLY].[magaga].[MATCHES] B ON A.match_id = B.match_id
 LEFT JOIN [AOE2_VOOBLY].[magaga].[INSTANCES] C ON A.match_id = C.match_id AND A.instance_id = C.instance_id