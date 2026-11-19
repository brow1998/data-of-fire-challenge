-- Fails if an incident id present in raw is missing from the fact table, or vice versa.
select coalesce(r.id, f.incident_id) as incident_id
from (select distinct id from {{ source('raw', 'incidents') }}) as r
full outer join {{ ref('fct_fire_incidents') }} as f on f.incident_id = r.id
where r.id is null or f.incident_id is null
