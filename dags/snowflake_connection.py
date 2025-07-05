"""
Snowflake Connection and Monitoring DAG
This DAG tests Snowflake connectivity and monitors data source health
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
import logging

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

dag = DAG(
    'snowflake_monitoring',
    default_args=default_args,
    description='Snowflake Connection Monitoring and Health Checks',
    schedule_interval='0 */6 * * *',  # Every 6 hours
    max_active_runs=1,
    tags=['snowflake', 'monitoring', 'health-check'],
)

def test_snowflake_connection():
    """
    Test basic Snowflake connectivity
    """
    logger = logging.getLogger(__name__)
    logger.info("Testing Snowflake connection...")
    
    try:
        snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        result = snowflake_hook.get_first("SELECT CURRENT_TIMESTAMP(), CURRENT_USER(), CURRENT_ROLE()")
        logger.info(f"Connection successful - Time: {result[0]}, User: {result[1]}, Role: {result[2]}")
        return True
    except Exception as e:
        logger.error(f"Snowflake connection failed: {e}")
        raise

def check_warehouse_status():
    """
    Check Snowflake warehouse status and usage
    """
    logger = logging.getLogger(__name__)
    logger.info("Checking warehouse status...")
    
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    
    warehouse_query = """
    SELECT 
        warehouse_name,
        state,
        running,
        queued,
        provisioned_provisioning_time,
        suspended,
        suspended_time
    FROM information_schema.warehouses
    WHERE warehouse_name = 'COMPUTE_WH'
    """
    
    result = snowflake_hook.get_first(warehouse_query)
    logger.info(f"Warehouse Status - Name: {result[0]}, State: {result[1]}, Running: {result[2]}, Queued: {result[3]}")
    return True

def check_data_source_health():
    """
    Check health of all data sources
    """
    logger = logging.getLogger(__name__)
    logger.info("Checking data source health...")
    
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    
    # Check D365 data
    d365_health = """
    SELECT 
        'D365_CUSTOMERS' as source_name,
        COUNT(*) as record_count,
        MAX(updated_at) as latest_update,
        DATEDIFF('hour', MAX(updated_at), CURRENT_TIMESTAMP()) as hours_since_update
    FROM DBT_HOL_DEV.raw.D365_CUSTOMERS
    """
    
    d365_result = snowflake_hook.get_first(d365_health)
    logger.info(f"D365 Health - Records: {d365_result[1]}, Latest: {d365_result[2]}, Hours Since Update: {d365_result[3]}")
    
    # Check legacy data
    legacy_health = """
    SELECT 
        'EXCEL_DATA' as source_name,
        COUNT(*) as record_count,
        COUNT(CASE WHEN postal_code IS NOT NULL THEN 1 END) as complete_records,
        ROUND(COUNT(CASE WHEN postal_code IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as completeness_pct
    FROM DBT_HOL_DEV.raw.EXCEL_DATA
    """
    
    legacy_result = snowflake_hook.get_first(legacy_health)
    logger.info(f"Legacy Health - Records: {legacy_result[1]}, Complete: {legacy_result[2]}, Completeness: {legacy_result[3]}%")
    
    # Check weather data
    weather_health = """
    SELECT 
        'WEATHER_DATA' as source_name,
        COUNT(*) as record_count,
        MAX(date_valid_std) as latest_weather_date,
        COUNT(DISTINCT postal_code) as unique_locations
    FROM WEATHER_SOURCE_LLC_FROSTBYTE.ONPOINT_ID."forecast_day"
    WHERE date_valid_std >= CURRENT_DATE()
    """
    
    try:
        weather_result = snowflake_hook.get_first(weather_health)
        logger.info(f"Weather Health - Records: {weather_result[1]}, Latest Date: {weather_result[2]}, Locations: {weather_result[3]}")
    except Exception as e:
        logger.warning(f"Weather data health check failed: {e}")
    
    return True

def check_model_status():
    """
    Check status of dbt models
    """
    logger = logging.getLogger(__name__)
    logger.info("Checking dbt model status...")
    
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    
    # Check bronze models
    bronze_check = """
    SELECT 
        'bronze_customers' as model_name,
        COUNT(*) as record_count
    FROM raw_BRONZE_DEV.bronze_customers
    """
    
    bronze_result = snowflake_hook.get_first(bronze_check)
    logger.info(f"Bronze Customers - Records: {bronze_result[1]}")
    
    # Check silver models
    silver_check = """
    SELECT 
        'silver_customer_weather' as model_name,
        COUNT(*) as record_count,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM raw_SILVER_DEV.silver_customer_weather
    """
    
    silver_result = snowflake_hook.get_first(silver_check)
    logger.info(f"Silver Customer Weather - Records: {silver_result[1]}, Customers: {silver_result[2]}")
    
    # Check gold models
    gold_check = """
    SELECT 
        'gold_customer_kpis' as model_name,
        COUNT(*) as region_count,
        SUM(total_customers) as total_customers
    FROM raw_GOLD_DEV.gold_customer_kpis
    """
    
    gold_result = snowflake_hook.get_first(gold_check)
    logger.info(f"Gold Customer KPIs - Regions: {gold_result[1]}, Total Customers: {gold_result[2]}")
    
    return True

# Task definitions
test_connection_task = PythonOperator(
    task_id='test_snowflake_connection',
    python_callable=test_snowflake_connection,
    dag=dag,
)

check_warehouse_task = PythonOperator(
    task_id='check_warehouse_status',
    python_callable=check_warehouse_status,
    dag=dag,
)

check_data_health_task = PythonOperator(
    task_id='check_data_source_health',
    python_callable=check_data_source_health,
    dag=dag,
)

check_models_task = PythonOperator(
    task_id='check_model_status',
    python_callable=check_model_status,
    dag=dag,
)

# Task dependencies
test_connection_task >> check_warehouse_task >> check_data_health_task >> check_models_task 