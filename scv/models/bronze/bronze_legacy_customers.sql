{{ config(
    materialized='view'
) }}

SELECT * FROM {{ source('bronze', 'EXCEL_DATA') }}
