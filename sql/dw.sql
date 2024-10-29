CREATE TABLE dw.fact_fire_incidents (
    incident_number VARCHAR(20) PRIMARY KEY,
    exposure_number INT,
    incident_date DATE,
    estimated_property_loss DECIMAL(15, 2),
    estimated_contents_loss DECIMAL(15, 2),
    fire_fatalities INT,
    fire_injuries INT,
    civilian_fatalities INT,
    civilian_injuries INT,
    battalion VARCHAR(10),
    district VARCHAR(100)
);

CREATE TABLE dw.dim_time (
    time_id SERIAL PRIMARY KEY,
    year INT,
    quarter INT,
    month INT,
    day INT,
    week INT,
    day_of_week VARCHAR(10),
    incident_date DATE UNIQUE
);

CREATE TABLE dw.dim_district (
    district_id SERIAL PRIMARY KEY,
    district_name VARCHAR(100) UNIQUE
);

CREATE TABLE dw.dim_battalion (
    battalion_id SERIAL PRIMARY KEY,
    battalion_name VARCHAR(10) UNIQUE
);


