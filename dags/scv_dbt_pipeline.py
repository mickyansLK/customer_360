"""
SCV (Single Customer View) dbt Pipeline DAG
This DAG orchestrates the complete dbt pipeline for creating a unified customer view
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.utils.trigger_rule import TriggerRule
import logging
import os
import sys

# Add dbt path to Python path
sys.path.append('/opt/airflow/dbt')

# Default arguments for the DAG
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
dag = DAG(
    'scv_dbt_pipeline',
    default_args=default_args,
    description='SCV dbt Pipeline - Single Customer View with Weather Data',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    max_active_runs=1,
    tags=['dbt', 'scv', 'customer', 'weather', 'data-pipeline'],
    doc_md=__doc__,
)

# Task IDs for easy reference
TASK_IDS = {
    'start': 'start_pipeline',
    'validate_sources': 'validate_data_sources',
    'dbt_deps': 'install_dbt_dependencies',
    'dbt_seed': 'load_seed_data',
    'dbt_run': 'run_dbt_models',
    'dbt_test': 'run_dbt_tests',
    'dbt_docs': 'generate_dbt_docs',
    'validate_output': 'validate_pipeline_output',
    'notify_success': 'notify_success',
    'notify_failure': 'notify_failure',
    'end': 'end_pipeline',
}

def validate_data_sources():
    """
    Validate that all data sources are accessible and have fresh data
    """
    import logging
    from datetime import datetime, timedelta
    
    logger = logging.getLogger(__name__)
    logger.info("Starting data source validation...")
    
    # Snowflake connection
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    
    # Check D365 customers data
    d365_check_query = """
    SELECT 
        COUNT(*) as record_count,
        MAX(updated_at) as latest_update,
        CURRENT_TIMESTAMP() as check_time
    FROM DBT_HOL_DEV.raw.D365_CUSTOMERS
    WHERE updated_at >= DATEADD(day, -1, CURRENT_DATE())
    """
    
    d365_result = snowflake_hook.get_first(d365_check_query)
    logger.info(f"D365 Customers - Count: {d365_result[0]}, Latest Update: {d365_result[1]}")
    
    # Check legacy Excel data
    legacy_check_query = """
    SELECT 
        COUNT(*) as record_count,
        COUNT(CASE WHEN postal_code IS NOT NULL THEN 1 END) as records_with_postal,
        COUNT(CASE WHEN region IS NOT NULL THEN 1 END) as records_with_region
    FROM DBT_HOL_DEV.raw.EXCEL_DATA
    """
    
    legacy_result = snowflake_hook.get_first(legacy_check_query)
    logger.info(f"Legacy Data - Total: {legacy_result[0]}, With Postal: {legacy_result[1]}, With Region: {legacy_result[2]}")
    
    # Check weather data
    weather_check_query = """
    SELECT 
        COUNT(*) as record_count,
        MAX(date_valid_std) as latest_weather_date,
        COUNT(DISTINCT postal_code) as unique_locations
    FROM WEATHER_SOURCE_LLC_FROSTBYTE.ONPOINT_ID."forecast_day"
    WHERE date_valid_std >= CURRENT_DATE()
    """
    
    try:
        weather_result = snowflake_hook.get_first(weather_check_query)
        logger.info(f"Weather Data - Count: {weather_result[0]}, Latest Date: {weather_result[1]}, Locations: {weather_result[2]}")
    except Exception as e:
        logger.warning(f"Weather data check failed: {e}")
    
    # Validation criteria
    if d365_result[0] == 0:
        raise ValueError("No recent D365 customer data found")
    
    if legacy_result[1] < legacy_result[0] * 0.9:  # 90% should have postal codes
        logger.warning("Many legacy records missing postal codes")
    
    logger.info("Data source validation completed successfully")
    return True

def validate_pipeline_output():
    """
    Validate the final pipeline output and generate quality metrics
    """
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info("Starting pipeline output validation...")
    
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    
    # Check gold layer completeness
    gold_check_query = """
    SELECT 
        COUNT(*) as total_regions,
        SUM(total_customers) as total_customers,
        AVG(avg_temp_f) as avg_temperature,
        AVG(avg_rain_chance_pct) as avg_rain_chance
    FROM raw_GOLD_DEV.gold_customer_kpis
    """
    
    gold_result = snowflake_hook.get_first(gold_check_query)
    logger.info(f"Gold Layer - Regions: {gold_result[0]}, Customers: {gold_result[1]}, Avg Temp: {gold_result[2]}, Avg Rain: {gold_result[3]}")
    
    # Check silver layer completeness
    silver_check_query = """
    SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(CASE WHEN avg_temperature_air_2m_f IS NOT NULL THEN 1 END) as records_with_weather
    FROM raw_SILVER_DEV.silver_customer_weather
    """
    
    silver_result = snowflake_hook.get_first(silver_check_query)
    logger.info(f"Silver Layer - Records: {silver_result[0]}, Customers: {silver_result[1]}, With Weather: {silver_result[2]}")
    
    # Quality checks
    if gold_result[1] == 0:
        raise ValueError("No customers found in gold layer")
    
    weather_coverage = silver_result[2] / silver_result[1] if silver_result[1] > 0 else 0
    if weather_coverage < 0.7:  # At least 70% should have weather data
        logger.warning(f"Low weather data coverage: {weather_coverage:.2%}")
    
    logger.info("Pipeline output validation completed successfully")
    return True

def notify_success(context):
    """
    Send success notification
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("SCV Pipeline completed successfully!")
    # Add your notification logic here (Slack, email, etc.)
    return True

def notify_failure(context):
    """
    Send failure notification
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.error("SCV Pipeline failed!")
    # Add your notification logic here (Slack, email, etc.)
    return True

# Task definitions
start_task = DummyOperator(
    task_id=TASK_IDS['start'],
    dag=dag,
)

validate_sources_task = PythonOperator(
    task_id=TASK_IDS['validate_sources'],
    python_callable=validate_data_sources,
    dag=dag,
)

dbt_deps_task = BashOperator(
    task_id=TASK_IDS['dbt_deps'],
    bash_command='cd /opt/airflow/dbt/scv && dbt deps',
    dag=dag,
)

dbt_seed_task = BashOperator(
    task_id=TASK_IDS['dbt_seed'],
    bash_command='cd /opt/airflow/dbt/scv && dbt seed',
    dag=dag,
)

dbt_run_task = BashOperator(
    task_id=TASK_IDS['dbt_run'],
    bash_command='cd /opt/airflow/dbt/scv && dbt run --profiles-dir /opt/airflow/.dbt',
    dag=dag,
)

dbt_test_task = BashOperator(
    task_id=TASK_IDS['dbt_test'],
    bash_command='cd /opt/airflow/dbt/scv && dbt test --profiles-dir /opt/airflow/.dbt',
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)

dbt_docs_task = BashOperator(
    task_id=TASK_IDS['dbt_docs'],
    bash_command='cd /opt/airflow/dbt/scv && dbt docs generate --profiles-dir /opt/airflow/.dbt',
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)

validate_output_task = PythonOperator(
    task_id=TASK_IDS['validate_output'],
    python_callable=validate_pipeline_output,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)

notify_success_task = PythonOperator(
    task_id=TASK_IDS['notify_success'],
    python_callable=notify_success,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)

notify_failure_task = PythonOperator(
    task_id=TASK_IDS['notify_failure'],
    python_callable=notify_failure,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag,
)

end_task = DummyOperator(
    task_id=TASK_IDS['end'],
    trigger_rule=TriggerRule.NONE_FAILED,
    dag=dag,
)

# Task dependencies
start_task >> validate_sources_task >> dbt_deps_task >> dbt_seed_task >> dbt_run_task >> dbt_test_task

dbt_test_task >> [dbt_docs_task, validate_output_task]
dbt_docs_task >> validate_output_task
validate_output_task >> notify_success_task >> end_task

# Failure path
[dbt_run_task, dbt_test_task, validate_output_task] >> notify_failure_task >> end_task 