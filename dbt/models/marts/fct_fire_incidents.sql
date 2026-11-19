-- One row per incident. Every row points back at the raw record it came from.
select
    incident_id,
    incident_number,
    exposure_number,
    to_char(incident_date, 'YYYYMMDD')::integer           as date_key,
    coalesce(battalion_code, 'Unknown')                   as battalion_code,
    coalesce(neighborhood_district, 'Unknown')            as district_name,
    station_area,
    primary_situation,
    property_use,
    alarm_at,
    arrival_at,
    closed_at,
    -- Negative gaps exist in the source (arrival logged before alarm); they are not a response time.
    case when arrival_at >= alarm_at
        then round(extract(epoch from arrival_at - alarm_at) / 60.0, 2)
    end                                                   as response_minutes,
    number_of_alarms,
    suppression_units + ems_units                         as units_dispatched,
    fire_fatalities + civilian_fatalities                 as fatalities,
    fire_injuries + civilian_injuries                     as injuries,
    fire_fatalities,
    fire_injuries,
    civilian_fatalities,
    civilian_injuries,
    estimated_property_loss,
    estimated_contents_loss,
    data_as_of,
    source_page_id,
    source_row_number
from {{ ref('stg_fire__incidents') }}
