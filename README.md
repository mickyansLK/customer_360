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

## 🔍 Model Visualization & Lineage

### Interactive dbt Documentation
The project includes comprehensive model visualization and lineage tracking similar to dbt Cloud.

#### Start dbt Docs Server
```bash
cd scv
dbt docs generate
dbt docs serve --port 8081
```

**Access the documentation at**: http://localhost:8081

#### Features Available
- **Interactive Lineage Graph**: Visual representation of model dependencies
- **Model Documentation**: Detailed descriptions and column information
- **Test Results**: Data quality test outcomes and history
- **Source Documentation**: External table and source definitions
- **Execution History**: Model run timestamps and performance metrics

### Static Lineage Visualization
The project includes pre-generated lineage visualizations:

#### SVG Lineage Graph
- **File**: `scv/scv_lineage_graph.svg`
- **Content**: Complete data flow from sources to gold layer
- **Usage**: Open in any web browser or image viewer

#### Lineage Analysis Script
- **File**: `scv/lineage_analysis.py`
- **Purpose**: Programmatic lineage analysis and dependency matrix
- **Usage**: 
  ```bash
  cd scv
  python lineage_analysis.py
  ```

### VS Code Integration
For enhanced development experience with lineage visualization:

#### dbt Power User Extension
1. **Install Extension**: `innoverio.vscode-dbt-power-user`
2. **Configuration**: Already configured in `.vscode/settings.json`
3. **Features**:
   - Model tree view in VS Code sidebar
   - Hover documentation for models and columns
   - Go-to-definition for model references
   - Lineage panel showing upstream/downstream dependencies
   - Auto-completion for dbt functions and macros

#### Using VS Code for Lineage
- **View Model Tree**: Open VS Code sidebar → dbt Power User
- **See Dependencies**: Hover over model names to see lineage
- **Navigate Models**: Ctrl+Click on model references
- **Lineage Panel**: View upstream/downstream models in real-time

### Lineage Graph Structure

![SCV Data Lineage](scv/scv_lineage_graph.svg)

**Data Flow**: Sources → Bronze Layer → Silver Layer → Gold Layer

```
Sources → Bronze Layer → Silver Layer → Gold Layer
   ↓           ↓            ↓           ↓
D365_CUSTOMERS → bronze_customers → silver_customer_weather → gold_customer_kpis
EXCEL_DATA → bronze_legacy_customers ↗
forecast_day → bronze_weather ↗
```

### Model Dependencies
- **bronze_customers**: Depends on D365_CUSTOMERS source
- **bronze_legacy_customers**: Depends on EXCEL_DATA source  
- **bronze_weather**: Depends on forecast_day source
- **silver_customer_weather**: Depends on bronze_customers and bronze_weather
- **gold_customer_kpis**: Depends on silver_customer_weather

### Troubleshooting Visualization
1. **dbt Docs Not Loading**: Ensure you're in the `scv` directory
2. **Port Already in Use**: Use different port: `dbt docs serve --port 8082`
3. **VS Code Extension Issues**: Reload VS Code window
4. **Lineage Not Updating**: Run `dbt docs generate` after model changes

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