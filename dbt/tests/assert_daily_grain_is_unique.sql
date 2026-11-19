select date_key, district_name, battalion_code
from {{ ref('agg_incidents_daily') }}
group by 1, 2, 3
having count(*) > 1
