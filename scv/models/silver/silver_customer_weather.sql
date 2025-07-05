{{ config(
    materialized='table', 
    enabled=True,
    on_schema_change='sync_all_columns'
) }}

-- Enhanced silver layer combining customer data with weather forecasts
-- This model joins customer data with weather data for location-based analysis
-- Includes error handling, data quality checks, and debugging capabilities

{{ log("Starting execution of model: silver_customer_weather", info=true) }}

WITH customer_data AS (
    SELECT 
        customer_id,
        first_name,
        last_name,
        postal_code,
        region,
        email,
        created_at,
        updated_at
    FROM {{ ref('bronze_customers') }}
    WHERE postal_code IS NOT NULL  -- Ensure we have location data for weather join
),

weather_data AS (
    SELECT 
        postal_code,
        date_valid_std,
        -- Handle missing weather data
        COALESCE(avg_temperature_air_2m_f, 0) as avg_temperature_air_2m_f,
        COALESCE(probability_of_precipitation_pct, 0) as probability_of_precipitation_pct,
        avg_humidity_relative_2m_pct,
        avg_wind_speed_10m_mph,
        tot_precipitation_in,
        tot_snowfall_in,
        avg_cloud_cover_tot_pct,
        probability_of_snow_pct
    FROM {{ ref('bronze_weather') }}
    WHERE date_valid_std >= CURRENT_DATE() - 7  -- Only include recent weather data
),

joined_data AS (
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        c.postal_code,
        c.region,
        c.email,
        w.date_valid_std,
        w.avg_temperature_air_2m_f,
        w.probability_of_precipitation_pct,
        w.avg_humidity_relative_2m_pct,
        w.avg_wind_speed_10m_mph,
        w.tot_precipitation_in,
        w.tot_snowfall_in,
        w.avg_cloud_cover_tot_pct,
        w.probability_of_snow_pct,
        -- Add audit columns
        CURRENT_TIMESTAMP() as _dbt_loaded_at,
        -- Add data quality indicators
        CASE 
            WHEN w.postal_code IS NULL THEN 'No weather data available'
            WHEN w.avg_temperature_air_2m_f IS NULL THEN 'Missing temperature data'
            WHEN w.probability_of_precipitation_pct IS NULL THEN 'Missing precipitation data'
            ELSE 'Complete data'
        END as data_completeness_status
    FROM customer_data c
    LEFT JOIN weather_data w
        ON c.postal_code = w.postal_code
)

SELECT 
    customer_id,
    first_name,
    last_name,
    postal_code,
    region,
    email,
    date_valid_std,
    avg_temperature_air_2m_f,
    probability_of_precipitation_pct,
    avg_humidity_relative_2m_pct,
    avg_wind_speed_10m_mph,
    tot_precipitation_in,
    tot_snowfall_in,
    avg_cloud_cover_tot_pct,
    probability_of_snow_pct,
    _dbt_loaded_at,
    data_completeness_status
FROM joined_data
WHERE customer_id IS NOT NULL  -- Ensure we have valid customer data

{{ log("Completed execution of model: silver_customer_weather", info=true) }}
