-- Audit helper macros for SCV project
-- These macros provide debugging and error handling capabilities

{% macro log_model_start(model_name) %}
    -- Log the start of model execution for debugging
    {{ log("Starting execution of model: " ~ model_name, info=true) }}
    {{ log("Execution timestamp: " ~ modules.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), info=true) }}
{% endmacro %}

{% macro log_model_end(model_name, rows_affected) %}
    -- Log the completion of model execution
    {{ log("Completed execution of model: " ~ model_name, info=true) }}
    {{ log("Rows affected: " ~ rows_affected, info=true) }}
    {{ log("Completion timestamp: " ~ modules.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), info=true) }}
{% endmacro %}

{% macro validate_not_empty(model_name, query) %}
    -- Validate that a query returns at least one row
    {% set result = run_query(query) %}
    {% if result.rows | length == 0 %}
        {{ exceptions.raise_compiler_error("Model " ~ model_name ~ " returned no rows. This may indicate a data quality issue.") }}
    {% endif %}
    {{ log("Model " ~ model_name ~ " validation passed - returned " ~ result.rows | length ~ " rows", info=true) }}
{% endmacro %}

{% macro check_data_freshness(source_name, table_name, date_column, max_hours_old=24) %}
    -- Check if data is fresh (not older than specified hours)
    {% set query %}
        SELECT 
            MAX({{ date_column }}) as latest_date,
            CURRENT_TIMESTAMP() as current_time,
            DATEDIFF('hour', MAX({{ date_column }}), CURRENT_TIMESTAMP()) as hours_old
        FROM {{ source(source_name, table_name) }}
        WHERE {{ date_column }} IS NOT NULL
    {% endset %}
    
    {% set result = run_query(query) %}
    {% if result.rows | length > 0 %}
        {% set hours_old = result.rows[0][2] %}
        {% if hours_old > max_hours_old %}
            {{ log("WARNING: Data in " ~ source_name ~ "." ~ table_name ~ " is " ~ hours_old ~ " hours old (max allowed: " ~ max_hours_old ~ ")", info=true) }}
        {% else %}
            {{ log("Data freshness check passed for " ~ source_name ~ "." ~ table_name ~ " - " ~ hours_old ~ " hours old", info=true) }}
        {% endif %}
    {% endif %}
{% endmacro %}

{% macro add_audit_columns() %}
    -- Add standard audit columns to models
    _dbt_run_at as created_at,
    CURRENT_TIMESTAMP() as updated_at
{% endmacro %}

{% macro handle_missing_weather_data() %}
    -- Handle cases where weather data is missing for customer locations
    COALESCE(w.avg_temperature_air_2m_f, 0) as avg_temperature_air_2m_f,
    COALESCE(w.probability_of_precipitation_pct, 0) as probability_of_precipitation_pct
{% endmacro %}

{% macro validate_postal_code(postal_code_column) %}
    -- Validate postal code format and log issues
    CASE 
        WHEN {{ postal_code_column }} REGEXP '^[0-9]{5}$' THEN {{ postal_code_column }}
        WHEN {{ postal_code_column }} IS NULL THEN NULL
        ELSE 
            {{ log("Invalid postal code format found: " ~ postal_code_column, info=true) }}
            NULL
    END as validated_postal_code
{% endmacro %}

{% macro log_data_quality_issues(model_name, column_name, condition, severity='info') %}
    -- Log data quality issues for monitoring
    {% set query %}
        SELECT COUNT(*) as issue_count
        FROM {{ ref(model_name) }}
        WHERE {{ condition }}
    {% endset %}
    
    {% set result = run_query(query) %}
    {% if result.rows | length > 0 %}
        {% set issue_count = result.rows[0][0] %}
        {% if issue_count > 0 %}
            {{ log("DATA QUALITY ISSUE: " ~ issue_count ~ " records in " ~ model_name ~ "." ~ column_name ~ " failed validation", info=true) }}
        {% endif %}
    {% endif %}
{% endmacro %}

{% macro create_error_log_table() %}
    -- Create error log table for tracking data quality issues
    {% if execute %}
        {% set create_table_sql %}
            CREATE TABLE IF NOT EXISTS {{ target.database }}.{{ target.schema }}.error_log (
                error_id NUMBER AUTOINCREMENT,
                model_name STRING,
                error_type STRING,
                error_message STRING,
                affected_rows NUMBER,
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        {% endset %}
        {{ run_query(create_table_sql) }}
    {% endif %}
{% endmacro %}

{% macro log_error(model_name, error_type, error_message, affected_rows=0) %}
    -- Log errors to the error log table
    {% set insert_sql %}
        INSERT INTO {{ target.database }}.{{ target.schema }}.error_log 
        (model_name, error_type, error_message, affected_rows)
        VALUES ('{{ model_name }}', '{{ error_type }}', '{{ error_message }}', {{ affected_rows }})
    {% endset %}
    {{ run_query(insert_sql) }}
{% endmacro %}

{% macro get_model_stats(model_name) %}
    -- Get statistics about a model for monitoring
    {% set query %}
        SELECT 
            COUNT(*) as total_rows,
            COUNT(DISTINCT customer_id) as unique_customers,
            MIN(created_at) as earliest_record,
            MAX(created_at) as latest_record
        FROM {{ ref(model_name) }}
    {% endset %}
    
    {% set result = run_query(query) %}
    {% if result.rows | length > 0 %}
        {% set stats = result.rows[0] %}
        {{ log("Model " ~ model_name ~ " stats - Total rows: " ~ stats[0] ~ ", Unique customers: " ~ stats[1], info=true) }}
    {% endif %}
{% endmacro %} 