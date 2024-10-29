SELECT 
    dt.year, 
    dt.month, 
    dd.district_name, 
    COUNT(fi.incident_number) AS total_incidents
FROM 
    dw.fact_fire_incidents fi
JOIN 
    dw.dim_time dt ON fi.incident_date = dt.incident_date
JOIN 
    dw.dim_district dd ON fi.district = dd.district_name
GROUP BY 
    dt.year, dt.month, dd.district_name
ORDER BY 
    dt.year, dt.month, dd.district_name;

   
   SELECT 
    db.battalion_name,
    SUM(fi.fire_fatalities) AS total_fatalities,
    SUM(fi.fire_injuries) AS total_injuries
FROM 
    dw.fact_fire_incidents fi
JOIN 
    dw.dim_battalion db ON fi.battalion = db.battalion_name
GROUP BY 
    db.battalion_name
ORDER BY 
    total_fatalities DESC;
