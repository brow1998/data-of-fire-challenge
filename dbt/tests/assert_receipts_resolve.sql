-- Fails if a fact row's receipt does not point at a raw record with the same id.
select f.incident_id
from {{ ref('fct_fire_incidents') }} as f
left join {{ source('raw', 'incidents') }} as r
    on r.page_id = f.source_page_id and r.row_number = f.source_row_number
where r.id is distinct from f.incident_id
