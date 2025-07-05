# SCV (Single Customer View) Project

## Overview

The SCV project is a dbt-based data pipeline that creates a unified customer view by combining customer data from multiple sources with weather data. This enables location-based customer analytics and weather-driven business insights.

## 🏗️ Architecture

The project follows a modern data architecture with three distinct layers:

### Bronze Layer (Raw Data)
- **bronze_customers**: Cleaned D365 customer data
- **bronze_legacy_customers**: Cleaned legacy Excel customer data
- **bronze_weather**: Weather forecast data from Snowflake Marketplace

### Silver Layer (Cleaned/Transformed Data)
- **silver_customer_weather**: Joined customer and weather data with data quality checks

### Gold Layer (Business Logic)
- **gold_customer_kpis**: Regional customer KPIs with weather metrics and business intelligence

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- dbt CLI
- Snowflake account with appropriate permissions
- Access to Snowflake Marketplace (Weather Source LLC Frostbyte)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SCV_poc
   ```

2. **Install dbt and dependencies**
   ```bash
   pip install dbt-snowflake
   cd scv
   dbt deps
   ```

3. **Configure your Snowflake connection**
   Create a `~/.dbt/profiles.yml` file:
   ```yaml
   scv:
     target: dev
     outputs:
       dev:
         type: snowflake
         account: your-snowflake-account
         user: your-username
         password: your-password
         role: your-role
         database: DBT_HOL_DEV
         warehouse: your-warehouse
         schema: raw_BRONZE_DEV
         threads: 4
   ```

4. **Run the pipeline**
   ```bash
   dbt run
   ```

5. **Run tests**
   ```bash
   dbt test
   ```

6. **Generate documentation**
   ```bash
   dbt docs generate
   dbt docs serve
   ```

## 📊 Data Sources

### Customer Data
- **D365 Customers**: Modern customer data from Dynamics 365 via ADLS Gen2
- **Legacy Excel Data**: Historical customer data from Excel files

### Weather Data
- **Snowflake Marketplace**: Weather forecast data from Weather Source LLC Frostbyte
- **Data Includes**: Temperature, humidity, wind speed, precipitation, snowfall, cloud cover

## 🔧 Configuration

### Environment Configuration
The project supports multiple environments through dbt targets:

- **Development**: Uses DEV schemas (BRONZE_DEV, SILVER_DEV, GOLD_DEV)
- **Production**: Uses PROD schemas (BRONZE, SILVER, GOLD)

### Model Configuration
Models are configured in `dbt_project.yml`:
- Bronze layer: Materialized as views
- Silver layer: Materialized as tables
- Gold layer: Materialized as tables

## 🧪 Testing

### Generic Tests
The project includes comprehensive data quality tests:
- **Unique**: Ensures no duplicate values
- **Not Null**: Validates required fields
- **Relationships**: Checks referential integrity
- **Accepted Range**: Validates numeric ranges

### Custom Tests
Custom business logic tests are implemented in `tests/test_data_quality.sql`:
- Email format validation
- Postal code format validation
- Data freshness checks
- Duplicate customer detection
- Weather data completeness

### Running Tests
```bash
# Run all tests
dbt test

# Run specific test
dbt test --select test_name

# Run tests for specific model
dbt test --select model_name
```

## 📈 Monitoring and Observability

### Logging
- Comprehensive logging throughout the pipeline
- Debug information for troubleshooting
- Performance metrics tracking

### Data Quality Monitoring
- Automated data quality checks
- Error logging and alerting
- Data completeness tracking

### Audit Trail
- Model execution timestamps
- Row count tracking
- Data quality status indicators

## 🔒 Security

### Access Control
- Role-based access control in Snowflake
- Secure credential management
- Audit logging for data access

### Data Protection
- Encryption at rest and in transit
- Sensitive data handling
- Compliance with data protection regulations

## 🚨 Troubleshooting

### Common Issues

1. **Weather Data Access Error**
   ```
   Object 'WEATHER_SOURCE_LLC_FROSTBYTE.ONPOINT_ID."forecast_day"' does not exist or not authorized.
   ```
   **Solution**: Verify Snowflake Marketplace access and permissions

2. **Data Quality Test Failures**
   - Check source data quality
   - Review test configurations
   - Validate business rules

3. **Performance Issues**
   - Monitor warehouse size and scaling
   - Review query optimization
   - Check resource utilization

### Debug Commands
```bash
# Test connection
dbt debug

# Check model dependencies
dbt ls --select model_name

# View compiled SQL
dbt compile --select model_name

# Check model status
dbt run --select model_name --dry-run
```

## 📚 Documentation

### Project Documentation
- **project_structure.md**: Detailed project architecture
- **rules.md**: Coding standards and best practices
- **tools.md**: Technology stack and tools
- **PRODUCTION_READINESS_AUDIT.md**: Production readiness assessment

### dbt Documentation
- Auto-generated documentation from schema files
- Data lineage graphs
- Model descriptions and column documentation

## 🔄 CI/CD

### Recommended Setup
- GitHub Actions for automated testing
- dbt Cloud for orchestration
- Automated deployment pipelines

### Deployment Process
1. Code review and testing
2. Automated test execution
3. Staging environment validation
4. Production deployment

## 📊 Business Value

### Customer Insights
- Unified customer view across systems
- Location-based customer segmentation
- Weather-driven customer behavior analysis

### Operational Benefits
- Automated data quality monitoring
- Reduced manual data processing
- Improved data accuracy and consistency

### Analytics Capabilities
- Regional customer KPIs
- Weather impact analysis
- Customer segmentation by weather conditions

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit pull request
5. Code review and approval

### Code Standards
- Follow SQL coding standards in `rules.md`
- Add comprehensive comments
- Include data quality tests
- Update documentation

## 📞 Support

### Getting Help
- Review troubleshooting section
- Check project documentation
- Consult dbt documentation
- Contact data engineering team

### Reporting Issues
- Create detailed issue reports
- Include error messages and logs
- Provide reproduction steps
- Specify environment details

## 📄 License

This project is proprietary and confidential. All rights reserved.

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainer**: Data Engineering Team 