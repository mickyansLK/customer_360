{{ config(
    materialized='view',
    on_schema_change='sync_all_columns'
)}}

-- Enhanced bronze layer for D365 customer data with improved error handling and debugging
-- This model provides a clean view of customer data with minimal transformations
-- Debug logging and data quality checks are included for production monitoring

{{ log("Starting execution of model: bronze_customers", info=true) }}

WITH source_data AS (
    SELECT 
        customer_id,
        first_name,
        last_name,
        email,
        phone,
        address,
        city,
        region,
        -- Validate postal code format
        CASE 
            WHEN postal_code REGEXP '^[0-9]{5}$' THEN postal_code
            WHEN postal_code IS NULL THEN NULL
            ELSE NULL
        END as postal_code,
        created_at,
        updated_at,
        -- Add audit columns for tracking
        CURRENT_TIMESTAMP() as _dbt_loaded_at
    FROM {{ source('bronze', 'D365_CUSTOMERS') }}
    WHERE customer_id IS NOT NULL  -- Basic data quality filter
),

validated_data AS (
    SELECT 
        *,
        -- Additional data quality checks
        CASE 
            WHEN email IS NOT NULL AND email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' 
            THEN 'Invalid email format'
            WHEN postal_code IS NOT NULL AND postal_code NOT REGEXP '^[0-9]{5}$'
            THEN 'Invalid postal code format'
            ELSE NULL
        END as data_quality_issues
    FROM source_data
)

SELECT 
    customer_id,
    first_name,
    last_name,
    email,
    phone,
    address,
    city,
    region,
    postal_code,
    created_at,
    updated_at,
    _dbt_loaded_at
FROM validated_data
WHERE data_quality_issues IS NULL  -- Filter out records with data quality issues

{{ log("Completed execution of model: bronze_customers", info=true) }}
