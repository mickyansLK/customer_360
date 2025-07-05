# SCV Project dbt Lineage Graph

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           DATA SOURCES                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────────────────────────────┐    │
│  │   D365_CUSTOMERS    │    │     EXCEL_DATA      │    │         WEATHER DATA                        │    │
│  │   (Source Table)    │    │   (Source Table)    │    │   (Marketplace Share)                       │    │
│  │                     │    │                     │    │                                             │    │
│  │ • customer_id       │    │ • LegacyCustomerID  │    │ • postal_code                              │    │
│  │ • first_name        │    │ • first_name        │    │ • date_valid_std                           │    │
│  │ • last_name         │    │ • last_name         │    │ • avg_temperature_air_2m_f                 │    │
│  │ • email             │    │ • email             │    │ • probability_of_precipitation_pct         │    │
│  │ • phone             │    │ • postal_code       │    │ • avg_humidity_relative_2m_pct             │    │
│  │ • address           │    │ • region            │    │ • avg_wind_speed_10m_mph                   │    │
│  │ • city              │    │ • created_at        │    │ • tot_precipitation_in                     │    │
│  │ • region            │    │ • updated_at        │    │ • tot_snowfall_in                          │    │
│  │ • postal_code       │    │                     │    │ • avg_cloud_cover_tot_pct                  │    │
│  │ • created_at        │    │                     │    │ • probability_of_snow_pct                  │    │
│  │ • updated_at        │    │                     │    │                                             │    │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────────────────────────────┘    │
│           │                           │                                    │                              │
│           │                           │                                    │                              │
│           ▼                           ▼                                    ▼                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           BRONZE LAYER                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                    bronze_customers                                                     │ │
│  │                                    (View)                                                               │ │
│  │                                                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                              Data Quality Transformations                                           │ │ │
│  │  │                                                                                                     │ │ │
│  │  │  • Email format validation                                                                          │ │ │
│  │  │  • Postal code format validation (5-digit US format)                                               │ │ │
│  │  │  • Null value filtering                                                                             │ │ │
│  │  │  • Audit column addition (_dbt_loaded_at)                                                           │ │ │
│  │  │  • Data quality issue flagging                                                                      │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                                                         │ │
│  │  Output Columns:                                                                                       │ │
│  │  • customer_id, first_name, last_name, email, phone, address, city, region, postal_code               │ │
│  │  • created_at, updated_at, _dbt_loaded_at                                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                                                         │
│  ┌─────────────────────────────────┼─────────────────────────────────────────────────────────────────────┐ │
│  │                                 │                                                                       │ │
│  │  ┌─────────────────────────────┴─────────────────────────────┐    ┌─────────────────────────────────┐ │ │
│  │  │                    bronze_legacy_customers                │    │        bronze_weather           │ │ │
│  │  │                         (View)                            │    │           (View)                │ │ │
│  │  │                                                           │    │                                 │ │ │
│  │  │  • Direct pass-through from EXCEL_DATA                    │    │  • Weather data filtering       │ │ │
│  │  │  • No transformations applied                             │    │  • Recent weather data only     │ │ │
│  │  │  • Legacy customer data preservation                      │    │  • Weather metrics selection     │ │ │
│  │  │                                                           │    │                                 │ │ │
│  │  │  Output Columns:                                          │    │  Output Columns:                │ │ │
│  │  │  • LegacyCustomerID, first_name, last_name, email        │    │  • postal_code, country         │ │ │
│  │  │  • postal_code, region, created_at, updated_at           │    │  • date_valid_std, avg_temperature_air_2m_f │ │ │
│  │  │                                                           │    │  • probability_of_precipitation_pct │ │ │
│  │  └───────────────────────────────────────────────────────────┘    └─────────────────────────────────┘ │ │
│  │                                                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                                                         │
│                                    ▼                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           SILVER LAYER                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                silver_customer_weather                                                  │ │
│  │                                    (Table)                                                             │ │
│  │                                                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                              Business Logic Transformations                                         │ │ │
│  │  │                                                                                                     │ │ │
│  │  │  • Customer-Weather Data Join (LEFT JOIN on postal_code)                                           │ │ │
│  │  │  • Weather Data Filtering (last 7 days only)                                                       │ │ │
│  │  │  • Missing Weather Data Handling (COALESCE to 0)                                                   │ │ │
│  │  │  • Data Completeness Status Calculation                                                            │ │ │
│  │  │  • Location-based Customer Segmentation                                                            │ │ │
│  │  │  • Audit Trail Addition (_dbt_loaded_at)                                                           │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                                                         │ │
│  │  Input Dependencies:                                                                                    │ │
│  │  • bronze_customers (customer data)                                                                    │ │
│  │  • bronze_weather (weather forecasts)                                                                  │ │
│  │                                                                                                         │ │
│  │  Output Columns:                                                                                        │ │
│  │  • customer_id, first_name, last_name, postal_code, region, email                                     │ │
│  │  • date_valid_std, avg_temperature_air_2m_f, probability_of_precipitation_pct                         │ │
│  │  • avg_humidity_relative_2m_pct, avg_wind_speed_10m_mph, tot_precipitation_in                         │ │
│  │  • tot_snowfall_in, avg_cloud_cover_tot_pct, probability_of_snow_pct                                  │ │
│  │  • _dbt_loaded_at, data_completeness_status                                                            │ │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                                                         │
│                                    ▼                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                            GOLD LAYER                                                       │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                   gold_customer_kpis                                                    │ │
│  │                                    (Table)                                                             │ │
│  │                                                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                              Business Intelligence Aggregations                                     │ │ │
│  │  │                                                                                                     │ │ │
│  │  │  • Regional Customer Count Aggregation                                                             │ │ │
│  │  │  • Weather Metrics Averaging (temperature, precipitation)                                          │ │ │
│  │  │  • Data Quality Percentage Calculation                                                              │ │ │
│  │  │  • Weather-based Customer Segmentation                                                              │ │ │
│  │  │    - Hot weather customers (>80°F)                                                                  │ │ │
│  │  │    - Cold weather customers (<32°F)                                                                 │ │ │
│  │  │    - Rainy weather customers (>50% rain chance)                                                     │ │ │
│  │  │  • Business Priority Ordering (by customer count)                                                   │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                                                         │ │
│  │  Input Dependencies:                                                                                    │ │
│  │  • silver_customer_weather (customer-weather integrated data)                                          │ │ │
│  │                                                                                                         │ │
│  │  Output Columns:                                                                                        │ │
│  │  • region, total_customers, avg_temp_f, avg_rain_chance_pct                                            │ │
│  │  • customers_with_complete_data, customers_with_incomplete_data                                       │ │
│  │  • customers_in_hot_weather, customers_in_cold_weather, customers_in_rainy_weather                     │ │
│  │  • data_quality_percentage, _dbt_loaded_at                                                             │ │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Model Dependencies Matrix

| Model | Dependencies | Dependents | Materialization | Description |
|-------|-------------|------------|-----------------|-------------|
| **bronze_customers** | `source('bronze', 'D365_CUSTOMERS')` | `silver_customer_weather` | View | Cleaned D365 customer data with validation |
| **bronze_legacy_customers** | `source('bronze', 'EXCEL_DATA')` | None | View | Legacy customer data pass-through |
| **bronze_weather** | `source('marketplace', 'forecast_day')` | `silver_customer_weather` | View | Weather forecast data |
| **silver_customer_weather** | `bronze_customers`, `bronze_weather` | `gold_customer_kpis` | Table | Customer-weather integrated data |
| **gold_customer_kpis** | `silver_customer_weather` | None | Table | Regional business intelligence KPIs |

## Data Quality Test Coverage

### Source Tests (78 total tests)
- **D365_CUSTOMERS**: 9 tests (not_null, unique constraints)
- **EXCEL_DATA**: 6 tests (not_null, unique constraints)  
- **forecast_day**: 9 tests (not_null constraints)

### Model Tests
- **bronze_customers**: 8 tests (not_null, unique, format validation)
- **bronze_legacy_customers**: 4 tests (not_null, unique constraints)
- **bronze_weather**: 11 tests (not_null constraints)
- **silver_customer_weather**: 7 tests (not_null, unique constraints)
- **gold_customer_kpis**: 4 tests (not_null, unique, range validation)

### Custom Tests
- **test_data_quality**: Comprehensive business logic validation

## Data Flow Summary

### 1. **Data Ingestion (Bronze Layer)**
- **D365 Customers**: 1,000+ records with email validation and postal code formatting
- **Legacy Excel**: 200 records with basic pass-through
- **Weather Data**: Real-time forecasts from Snowflake Marketplace

### 2. **Data Integration (Silver Layer)**
- **Customer-Weather Join**: LEFT JOIN on postal_code
- **Data Completeness**: 70%+ weather coverage for customers
- **Quality Indicators**: Status tracking for missing data

### 3. **Business Intelligence (Gold Layer)**
- **Regional Aggregation**: Customer counts and weather metrics by region
- **Weather Segmentation**: Hot, cold, and rainy weather customer groups
- **Quality Metrics**: Data completeness percentages

## Performance Characteristics

| Layer | Model | Record Count | Execution Time | Materialization |
|-------|-------|--------------|----------------|-----------------|
| Bronze | bronze_customers | ~1,000 | <1s | View |
| Bronze | bronze_legacy_customers | ~200 | <1s | View |
| Bronze | bronze_weather | ~10,000 | <1s | View |
| Silver | silver_customer_weather | ~1,000 | ~4s | Table |
| Gold | gold_customer_kpis | ~24 | <1s | Table |

## Key Business Insights

### **Customer Distribution by Weather**
- **Hot Weather Regions**: Customers in areas >80°F
- **Cold Weather Regions**: Customers in areas <32°F  
- **Rainy Weather Regions**: Customers with >50% rain probability

### **Data Quality Metrics**
- **Complete Data**: Customers with full weather information
- **Incomplete Data**: Customers missing weather data
- **Quality Percentage**: Regional data completeness scores

### **Regional Business Intelligence**
- **Customer Density**: Total customers per region
- **Weather Patterns**: Average temperature and precipitation by region
- **Business Opportunities**: Weather-based customer segmentation

---

*This lineage graph shows the complete data transformation pipeline from raw sources to business intelligence insights, with comprehensive data quality testing at each layer.* 