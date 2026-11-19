-- Every calendar day from the first to the last incident, so days without incidents still exist.
with bounds as (
    select min(incident_date) as first_day, max(incident_date) as last_day
    from {{ ref('stg_fire__incidents') }}
)

select
    to_char(d, 'YYYYMMDD')::integer      as date_key,
    d::date                              as date_day,
    extract(year from d)::integer        as year,
    extract(quarter from d)::integer     as quarter,
    extract(month from d)::integer       as month,
    to_char(d, 'FMMonth')                as month_name,
    date_trunc('month', d)::date         as month_start,
    extract(isoyear from d)::integer     as iso_year,
    extract(week from d)::integer        as iso_week,
    extract(isodow from d)::integer      as day_of_week,
    to_char(d, 'FMDay')                  as day_name,
    extract(isodow from d) in (6, 7)     as is_weekend
from bounds, generate_series(first_day, last_day, interval '1 day') as d
