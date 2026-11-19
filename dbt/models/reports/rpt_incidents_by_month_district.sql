select
    month_start,
    district_name,
    sum(incidents)    as incidents,
    sum(fatalities)   as fatalities,
    sum(injuries)     as injuries
from {{ ref('agg_incidents_daily') }}
group by 1, 2
