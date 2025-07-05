# Airflow Setup Guide for SCV Project

## Quick Start Guide

### Prerequisites
- Docker and Docker Compose installed
- Snowflake account with proper permissions
- SSH key for Snowflake authentication

### 1. Initial Setup

```bash
# Clone or navigate to your project directory
cd /home/micky/SCV_poc

# Create necessary directories (if not already created)
mkdir -p dags config logs plugins

# Copy your Snowflake credentials
cp ~/.snowsql/rsa_key.pem config/
chmod 600 config/rsa_key.pem
```

### 2. Start Airflow Services

```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f airflow-webserver
```

### 3. Access Airflow UI

- **Web UI**: http://localhost:8080
- **Default Credentials**: 
  - Username: `airflow`
  - Password: `airflow`
- **Flower (Monitoring)**: http://localhost:5555

### 4. Configure Snowflake Connection

1. Go to Admin → Connections in Airflow UI
2. Add new connection:
   - **Connection Id**: `snowflake_default`
   - **Connection Type**: `Snowflake`
   - **Host**: `your-account.snowflakecomputing.com`
   - **Login**: `your-username`
   - **Password**: (leave empty, using key authentication)
   - **Extra**: 
     ```json
     {
       "account": "your-snowflake-account",
       "warehouse": "your-warehouse",
       "database": "your-database",
       "role": "your-role",
       "private_key_path": "/opt/airflow/.snowsql/rsa_key.pem"
     }
     ```

### 5. Test the Setup

```bash
# Test dbt connection
docker-compose exec airflow-worker bash -c "cd /opt/airflow/dbt/scv && dbt debug"

# Test Snowflake connection
docker-compose exec airflow-worker bash -c "cd /opt/airflow/dbt/scv && dbt run --profiles-dir /opt/airflow/.dbt"
```

## DAG Overview

### Main Pipeline DAG: `scv_dbt_pipeline`
- **Schedule**: Daily at 2:00 AM
- **Tasks**:
  1. Validate data sources
  2. Install dbt dependencies
  3. Load seed data
  4. Run dbt models
  5. Execute data quality tests
  6. Generate documentation
  7. Validate output
  8. Send notifications

### Monitoring DAG: `snowflake_monitoring`
- **Schedule**: Every 6 hours
- **Tasks**:
  1. Test Snowflake connection
  2. Check warehouse status
  3. Monitor data source health
  4. Verify model status

## Troubleshooting

### Common Issues

1. **Permission Denied on SSH Key**
   ```bash
   chmod 600 config/rsa_key.pem
   ```

2. **dbt Profile Not Found**
   ```bash
   # Ensure profiles.yml is in the correct location
   ls -la config/dbt_profiles.yml
   ```

3. **Snowflake Connection Failed**
   - Verify account name and credentials
   - Check network connectivity
   - Ensure proper role permissions

4. **Airflow Services Not Starting**
   ```bash
   # Check logs
   docker-compose logs airflow-webserver
   docker-compose logs airflow-scheduler
   
   # Restart services
   docker-compose down
   docker-compose up -d
   ```

### Useful Commands

```bash
# View all logs
docker-compose logs -f

# Restart specific service
docker-compose restart airflow-webserver

# Execute commands in container
docker-compose exec airflow-worker bash

# Clean up volumes (WARNING: removes all data)
docker-compose down -v
```

## Production Deployment

### Environment Variables
Create `.env` file for production:
```bash
AIRFLOW__CORE__FERNET_KEY=your-fernet-key
AIRFLOW__WEBSERVER__SECRET_KEY=your-secret-key
SNOWFLAKE_ACCOUNT=your-snowflake-account
SNOWFLAKE_USER=your-username
SNOWFLAKE_ROLE=your-role
```

### Security Considerations
1. Change default Airflow passwords
2. Use environment variables for sensitive data
3. Enable SSL/TLS for all connections
4. Implement proper access controls
5. Regular security updates

### Monitoring Setup
1. Configure email/Slack notifications
2. Set up log aggregation
3. Implement health checks
4. Create operational dashboards

## Performance Optimization

### Airflow Configuration
- Adjust `parallelism` and `dag_concurrency`
- Configure proper resource limits
- Optimize database connections

### dbt Configuration
- Use incremental models for large datasets
- Implement proper partitioning
- Optimize warehouse sizing

### Snowflake Optimization
- Right-size warehouse for workload
- Use query acceleration
- Implement proper clustering

## Support and Maintenance

### Regular Maintenance
- Weekly: Review logs and performance
- Monthly: Update dependencies
- Quarterly: Security audit and updates

### Backup Procedures
- Airflow metadata database
- dbt project files
- Configuration files
- SSH keys and credentials

### Emergency Procedures
1. **Pipeline Failure**: Check logs, restart failed tasks
2. **Data Quality Issues**: Review test results, fix source data
3. **Infrastructure Issues**: Restart services, check resource usage
4. **Security Incidents**: Rotate credentials, audit access logs

---

*For additional support, refer to the project documentation or contact the data engineering team.* 