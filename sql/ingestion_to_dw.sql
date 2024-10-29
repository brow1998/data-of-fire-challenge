INSERT INTO dw.dim_district (district_name)
SELECT DISTINCT neighborhood_district
FROM fire_incidents
ON CONFLICT (district_name) DO NOTHING;

INSERT INTO dw.dim_battalion (battalion_name)
SELECT DISTINCT battalion
FROM fire_incidents
ON CONFLICT (battalion_name) DO NOTHING;

INSERT INTO dw.dim_time (year, quarter, month, day, week, day_of_week, incident_date)
SELECT DISTINCT 
    EXTRACT(YEAR FROM incident_date) AS year,
    EXTRACT(QUARTER FROM incident_date) AS quarter,
    EXTRACT(MONTH FROM incident_date) AS month,
    EXTRACT(DAY FROM incident_date) AS day,
    EXTRACT(WEEK FROM incident_date) AS week,
    TO_CHAR(incident_date, 'Day') AS day_of_week,
    incident_date
FROM fire_incidents
ON CONFLICT (incident_date) DO NOTHING;

INSERT INTO dw.fact_fire_incidents (incident_number, exposure_number, incident_date, estimated_property_loss, estimated_contents_loss, fire_fatalities, fire_injuries, civilian_fatalities, civilian_injuries, battalion, district)
SELECT 
    incident_number,
    exposure_number,
    incident_date,
    estimated_property_loss,
    estimated_contents_loss,
    fire_fatalities,
    fire_injuries,
    civilian_fatalities,
    civilian_injuries,
    battalion,
    neighborhood_district
FROM fire_incidents;
