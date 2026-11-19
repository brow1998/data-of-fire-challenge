-- One row per incident: the latest version we hold, typed and renamed.
with versions as (
    select
        i.page_id,
        i.row_number,
        i.record,
        row_number() over (
            partition by i.id
            order by i.data_as_of desc, p.fetched_at desc, i.page_id, i.row_number
        ) as version_rank
    from {{ source('raw', 'incidents') }} as i
    join {{ source('raw', 'pages') }} as p using (page_id)
)

select
    {{ text_field('id') }}                      as incident_id,
    {{ text_field('incident_number') }}         as incident_number,
    {{ int_field('exposure_number') }}          as exposure_number,
    ({{ text_field('incident_date') }})::date   as incident_date,
    {{ ts_field('alarm_dttm') }}                as alarm_at,
    {{ ts_field('arrival_dttm') }}              as arrival_at,
    {{ ts_field('close_dttm') }}                as closed_at,
    {{ text_field('address') }}                 as address,
    {{ text_field('zipcode') }}                 as zipcode,
    {{ text_field('battalion') }}               as battalion_code,
    {{ text_field('station_area') }}            as station_area,
    {{ text_field('neighborhood_district') }}   as neighborhood_district,
    {{ text_field('supervisor_district') }}     as supervisor_district,
    {{ text_field('primary_situation') }}       as primary_situation,
    {{ text_field('property_use') }}            as property_use,
    {{ int_field('number_of_alarms') }}         as number_of_alarms,
    {{ int_field('suppression_units') }}        as suppression_units,
    {{ int_field('suppression_personnel') }}    as suppression_personnel,
    {{ int_field('ems_units') }}                as ems_units,
    {{ int_field('ems_personnel') }}            as ems_personnel,
    coalesce({{ int_field('fire_fatalities') }}, 0)     as fire_fatalities,
    coalesce({{ int_field('fire_injuries') }}, 0)       as fire_injuries,
    coalesce({{ int_field('civilian_fatalities') }}, 0) as civilian_fatalities,
    coalesce({{ int_field('civilian_injuries') }}, 0)   as civilian_injuries,
    {{ money_field('estimated_property_loss') }}        as estimated_property_loss,
    {{ money_field('estimated_contents_loss') }}        as estimated_contents_loss,
    {{ ts_field('data_as_of') }}                as data_as_of,
    page_id                                     as source_page_id,
    row_number                                  as source_row_number
from versions
where version_rank = 1
