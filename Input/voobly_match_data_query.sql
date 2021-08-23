-- Ensure pool size is large enough to create the table

create table aoe2_voobly.match_data as
select ladder
      ,cast(Match_ID as unsigned) as Match_ID
      ,str_to_date(Match_date, '%m/%d/%Y') as Match_date
      ,str_to_date(Match_time , '%H:%i') as Match_time
      ,cast(Match_rating as unsigned) as Match_rating
      ,Match_map
      ,case when Match_length like '%:%' then round(time_to_sec(timediff(Match_length ,0))/60,0) else null end Match_length 
      ,cast(Match_player_no as unsigned) as Match_player_no
      ,Match_mod
      ,Player
      ,case when New_Rating = '' then null else cast(New_Rating as unsigned) end New_Rating 
      ,case when Points = '' then null else cast(Points as signed) end Points
      ,case when Team = '' then null else cast(Team as unsigned) end as Team
      ,Civilization
      ,case when Victory = '' then null else cast(Victory as unsigned) end as Victory
      ,case when Military_Score = '' then null else cast(replace(Military_Score,',','') as unsigned) end as Military_Score
	  ,case when Economy_Score = '' then null else cast(replace(Economy_Score,',','') as unsigned) end as Economy_Score
	  ,case when Technology_Score = '' then null else cast(replace(Technology_Score,',','') as unsigned) end as Technology_Score
	  ,case when Society_Score = '' then null else cast(replace(Society_Score,',','') as unsigned) end as Society_Score
	  ,case when Total_Score = '' then null else cast(replace(Total_Score,',','') as unsigned) end as Total_Score
	  ,case when Units_Killed = '' then null else cast(replace(Units_Killed,',','') as unsigned) end as Units_Killed
	  ,case when Units_Lost = '' then null else cast(replace(Units_Lost,',','') as unsigned) end as Units_Lost
	  ,case when Buildings_Razed = '' then null else cast(replace(Buildings_Razed,',','') as unsigned) end as Buildings_Razed
	  ,case when Buildings_Lost = '' then null else cast(replace(Buildings_Lost,',','') as unsigned) end as Buildings_Lost
	  ,case when Units_Converted = '' then null else cast(replace(Units_Converted,',','') as unsigned) end as Units_Converted
	  ,case when Food = '' then null else cast(replace(Food,',','') as unsigned) end as Food
	  ,case when Wood = '' then null else cast(replace(Wood,',','') as unsigned) end as Wood
	  ,case when Stone = '' then null else cast(replace(Stone,',','') as unsigned) end as Stone
	  ,case when Gold = '' then null else cast(replace(Gold,',','') as unsigned) end as Gold
	  ,case when Trade_Profit = '' then null else cast(replace(Trade_Profit,',','') as unsigned) end as Trade_Profit
	  ,case when Tribute_Received = '' then null else cast(replace(Tribute_Received,',','') as unsigned) end as Tribute_Received
	  ,case when Tribute_Sent = '' then null else cast(replace(Tribute_Sent,',','') as unsigned) end as Tribute_Sent
	  ,case when Feudal_Time <> 'n/a' then round(time_to_sec(timediff(Feudal_Time ,0))/60,0) else null end Feudal_Time
	  ,case when castle_Time <> 'n/a' then round(time_to_sec(timediff(castle_Time ,0))/60,0) else null end castle_Time
	  ,case when Imperial_Time <> 'n/a' then round(time_to_sec(timediff(Imperial_Time ,0))/60,0) else null end Imperial_Time
      ,round(cast(replace(Map_Explored,'%','') AS float)/100,4) as Map_Explored
      ,case when Research_Count = '' then null else cast(Research_Count as unsigned) end as Research_Count
      ,round(cast(replace(Research_Percent,'%','') AS float)/100,4) as Research_Percent
	  ,case when Total_Wonders = '' then null else cast(replace(Total_Wonders,',','') as unsigned) end as Total_Wonders
	  ,case when Total_castles = '' then null else cast(replace(Total_castles,',','') as unsigned) end as Total_castles
	  ,case when Relics_Captured = '' then null else cast(replace(Relics_Captured,',','') as unsigned) end as Relics_Captured
	  ,case when Relic_Gold = '' then null else cast(replace(Relic_Gold,',','') as unsigned) end as Relic_Gold
	  ,case when Villager_High = '' then null else cast(replace(Villager_High,',','') as unsigned) end as Villager_High
from aoe2_voobly.raw_match_data
