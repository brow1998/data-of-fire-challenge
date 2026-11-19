select
    d.year,
    f.battalion_code,
    count(*)                                                              as incidents,
    sum(f.fatalities)                                                     as fatalities,
    sum(f.injuries)                                                       as injuries,
    percentile_cont(0.5) within group (order by f.response_minutes)      as median_response_minutes
from {{ ref('fct_fire_incidents') }} as f
join {{ ref('dim_date') }} as d using (date_key)
group by 1, 2
