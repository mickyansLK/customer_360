{{ config(
    materialized='table',
    on_schema_change='sync_all_columns'
) }}

-- Enhanced gold layer with regional customer KPIs and weather metrics
-- This model provides business intelligence insights by region
-- Includes error handling, data quality checks, and debugging capabilities

{{ log("Starting execution of model: gold_customer_kpis", info=true) }}

WITH customer_weather_data AS (
    SELECT 
        region,
        customer_id,
        avg_temperature_air_2m_f,
        probability_of_precipitation_pct,
        data_completeness_status
    FROM {{ ref('silver_customer_weather') }}
    WHERE region IS NOT NULL  -- Ensure we have valid region data
),

regional_stats AS (
    SELECT
        region,
        COUNT(DISTINCT customer_id) AS total_customers,
        AVG(avg_temperature_air_2m_f) AS avg_temp_f,
        AVG(probability_of_precipitation_pct) AS avg_rain_chance_pct,
        -- Additional business metrics
        COUNT(CASE WHEN data_completeness_status = 'Complete data' THEN 1 END) as customers_with_complete_data,
        COUNT(CASE WHEN data_completeness_status != 'Complete data' THEN 1 END) as customers_with_incomplete_data,
        -- Weather-based customer segments
        COUNT(CASE WHEN avg_temperature_air_2m_f > 80 THEN 1 END) as customers_in_hot_weather,
        COUNT(CASE WHEN avg_temperature_air_2m_f < 32 THEN 1 END) as customers_in_cold_weather,
        COUNT(CASE WHEN probability_of_precipitation_pct > 50 THEN 1 END) as customers_in_rainy_weather
    FROM customer_weather_data
    GROUP BY region
),

final_kpis AS (
    SELECT
        region,
        total_customers,
        avg_temp_f,
        avg_rain_chance_pct,
        customers_with_complete_data,
        customers_with_incomplete_data,
        customers_in_hot_weather,
        customers_in_cold_weather,
        customers_in_rainy_weather,
        -- Calculate data quality percentage
        ROUND(
            (customers_with_complete_data::FLOAT / NULLIF(total_customers, 0)::FLOAT) * 100, 
            2
        ) as data_quality_percentage,
        -- Add audit columns
        CURRENT_TIMESTAMP() as _dbt_loaded_at
    FROM regional_stats
    WHERE total_customers > 0  -- Only include regions with customers
)

SELECT 
    region,
    total_customers,
    avg_temp_f,
    avg_rain_chance_pct,
    customers_with_complete_data,
    customers_with_incomplete_data,
    customers_in_hot_weather,
    customers_in_cold_weather,
    customers_in_rainy_weather,
    data_quality_percentage,
    _dbt_loaded_at
FROM final_kpis
ORDER BY total_customers DESC  -- Order by customer count for business priority

{{ log("Completed execution of model: gold_customer_kpis", info=true) }}
