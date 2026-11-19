-- The BI table: one row per day, district and battalion. Any period can be rolled up from here.
select
    f.date_key,
    d.date_day,
    d.year,
    d.quarter,
    d.month_start,
    d.iso_week,
    d.day_name,
    f.district_name,
    f.battalion_code,
    count(*)                                   as incidents,
    sum(f.fatalities)                          as fatalities,
    sum(f.injuries)                            as injuries,
    sum(f.estimated_property_loss)             as estimated_property_loss,
    round(avg(f.response_minutes), 2)          as avg_response_minutes
from {{ ref('fct_fire_incidents') }} as f
join {{ ref('dim_date') }} as d using (date_key)
group by 1, 2, 3, 4, 5, 6, 7, 8, 9
