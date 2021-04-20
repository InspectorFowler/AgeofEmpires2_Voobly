select 'Total' as ladder, 
	   count(*) as row_cnt,
	   count(distinct Match_ID) as match_cnt,
	   max(STR_TO_DATE(Match_date,'%m/%d/%Y')) as max_date,
	   min(STR_TO_DATE(Match_date,'%m/%d/%Y')) as min_date
from RAW_MATCH_DATA rmd

union

select ladder, 
	   count(*) as row_cnt,
	   count(distinct Match_ID) as match_cnt,
	   max(STR_TO_DATE(Match_date,'%m/%d/%Y')) as max_date,
	   min(STR_TO_DATE(Match_date,'%m/%d/%Y')) as min_date
from RAW_MATCH_DATA rmd
group by ladder
order by 3 desc

