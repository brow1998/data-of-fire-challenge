-- Neighborhood districts seen in the data, plus an explicit member for incidents without one.
select distinct coalesce(neighborhood_district, 'Unknown') as district_name
from {{ ref('stg_fire__incidents') }}
