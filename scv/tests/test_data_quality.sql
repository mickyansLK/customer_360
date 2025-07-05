-- Custom data quality tests for SCV project
-- These tests validate business logic and data integrity

-- Test 1: Ensure all customers have valid email addresses
-- This test checks that email addresses follow a basic email format
{{ config(severity = 'error') }}

SELECT 
    customer_id,
    email
FROM {{ ref('bronze_customers') }}
WHERE email IS NOT NULL 
  AND email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

-- Test 2: Validate postal code format (US 5-digit format)
-- This test ensures postal codes are in the expected format
{{ config(severity = 'warn') }}

SELECT 
    customer_id,
    postal_code
FROM {{ ref('bronze_customers') }}
WHERE postal_code IS NOT NULL 
  AND postal_code NOT REGEXP '^[0-9]{5}$'

-- Test 3: Check for duplicate customer records across sources
-- This test identifies potential duplicate customers between D365 and legacy data
{{ config(severity = 'error') }}

WITH d365_customers AS (
    SELECT DISTINCT customer_id, email, postal_code
    FROM {{ ref('bronze_customers') }}
),
legacy_customers AS (
    SELECT DISTINCT customer_id, email, postal_code
    FROM {{ ref('bronze_legacy_customers') }}
)
SELECT 
    'Potential duplicate customer' as issue_type,
    d.customer_id as d365_customer_id,
    l.customer_id as legacy_customer_id,
    d.email,
    d.postal_code
FROM d365_customers d
INNER JOIN legacy_customers l 
    ON d.email = l.email 
    AND d.postal_code = l.postal_code
WHERE d.customer_id != l.customer_id

-- Test 4: Validate weather data freshness
-- This test ensures weather data is not too old
{{ config(severity = 'error') }}

SELECT 
    postal_code,
    date_valid_std,
    CURRENT_DATE() as current_date,
    DATEDIFF('day', date_valid_std, CURRENT_DATE()) as days_old
FROM {{ ref('bronze_weather') }}
WHERE date_valid_std < DATEADD('day', -7, CURRENT_DATE())

-- Test 5: Check for customers without weather data
-- This test identifies customers whose locations don't have weather data
{{ config(severity = 'warn') }}

SELECT 
    c.customer_id,
    c.postal_code,
    c.region
FROM {{ ref('bronze_customers') }} c
LEFT JOIN {{ ref('bronze_weather') }} w 
    ON c.postal_code = w.postal_code
WHERE w.postal_code IS NULL

-- Test 6: Validate temperature ranges are reasonable
-- This test checks for extreme temperature values that might indicate data quality issues
{{ config(severity = 'error') }}

SELECT 
    postal_code,
    date_valid_std,
    avg_temperature_air_2m_f
FROM {{ ref('bronze_weather') }}
WHERE avg_temperature_air_2m_f < -50 
   OR avg_temperature_air_2m_f > 130

-- Test 7: Check for missing regions in gold layer
-- This test ensures all regions have customer data
{{ config(severity = 'warn') }}

SELECT 
    region,
    total_customers
FROM {{ ref('gold_customer_kpis') }}
WHERE total_customers = 0

-- Test 8: Validate data completeness in silver layer
-- This test ensures the silver layer has the expected number of records
{{ config(severity = 'error') }}

WITH customer_count AS (
    SELECT COUNT(*) as customer_count
    FROM {{ ref('bronze_customers') }}
),
silver_count AS (
    SELECT COUNT(*) as silver_count
    FROM {{ ref('silver_customer_weather') }}
)
SELECT 
    'Data completeness check failed' as issue,
    c.customer_count as expected_customers,
    s.silver_count as actual_silver_records
FROM customer_count c
CROSS JOIN silver_count s
WHERE s.silver_count < c.customer_count * 0.9  -- Allow 10% missing due to weather data gaps 