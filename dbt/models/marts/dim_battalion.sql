-- Battalions seen in the data, plus an explicit member for incidents without one.
select distinct coalesce(battalion_code, 'Unknown') as battalion_code
from {{ ref('stg_fire__incidents') }}
