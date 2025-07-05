# SCV (Single Customer View) Project Structure

## Overview
This is a dbt-based data pipeline project that creates a unified customer view by combining customer data from multiple sources with weather data.

## Project Architecture

### Directory Structure
```
SCV_poc/
├── scv/                    # Main dbt project
│   ├── models/            # Data transformation models
│   │   ├── bronze/        # Raw data layer (views)
│   │   ├── silver/        # Cleaned/transformed data layer (tables)
│   │   └── gold/          # Business logic layer (tables)
│   ├── tests/             # Data quality tests
│   ├── macros/            # Reusable SQL macros
│   ├── seeds/             # Static data files
│   ├── snapshots/         # Slowly changing dimensions
│   ├── analyses/          # Ad-hoc analyses
│   ├── logs/              # dbt execution logs
│   ├── target/            # Compiled artifacts
│   ├── dbt_packages/      # External packages
│   ├── dbt_project.yml    # Project configuration
│   ├── packages.yml       # Package dependencies
│   └── schema_test.yml    # Global schema tests
├── sql/                   # Additional SQL scripts
├── data/                  # Sample data files
│   ├── d365_fake_data.csv
│   ├── legacy_excel_data.csv
│   └── snowflake_marketplace_weather.csv
└── docs/                  # Documentation (to be created)
```

## Data Pipeline Architecture

### Bronze Layer (Raw Data)
- **bronze_customers.sql**: Views on D365 customer data
- **bronze_legacy_customers.sql**: Views on legacy Excel customer data  
- **bronze_weather.sql**: Views on weather forecast data

### Silver Layer (Cleaned Data)
- **silver_customer_weather.sql**: Joined customer and weather data

### Gold Layer (Business Logic)
- **gold_customer_kpis.sql**: Regional customer KPIs with weather metrics

## Data Sources
1. **D365 Customers**: Modern customer data from Dynamics 365
2. **Legacy Excel Data**: Historical customer data from Excel files
3. **Weather Data**: External weather forecast data from Snowflake Marketplace

## Current Status
- ✅ Basic dbt project structure implemented
- ✅ Bronze layer models created
- ✅ Silver and Gold layer models defined
- ❌ Missing data quality tests
- ❌ Missing documentation
- ❌ Missing error handling
- ❌ Missing production configurations
- ❌ Weather data source access issues

## Technology Stack
- **dbt**: 1.9.4
- **Database**: Snowflake
- **Packages**: dbt_utils 1.3.0
- **Data Sources**: Snowflake Marketplace, ADLS, Excel

## Environment Configuration
- **Development**: Uses DEV schemas (BRONZE_DEV, SILVER_DEV, GOLD_DEV)
- **Production**: Uses PROD schemas (BRONZE, SILVER, GOLD)
- **Materialization**: Bronze (views), Silver/Gold (tables) 