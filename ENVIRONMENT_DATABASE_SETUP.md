# Environment-Based Database Configuration

This document describes the environment-based database configuration and dummy data generation functionality implemented for the TAP (Timeclock and payroll) application.

## Overview

The application now automatically detects whether it's running in a development or production environment and creates/uses separate SQLite databases accordingly. In development mode, it also generates dummy data to help with development and testing.

## Features

### 🗄️ Environment-Aware Database Configuration
- **Development**: Uses `tap_dev.sqlite`
- **Production**: Uses `tap_prod.sqlite` 
- **Custom**: Support for custom database URLs via environment variable

### 🧪 Automatic Dummy Data Generation
- **Development Only**: Generates sample data automatically
- **Production Safe**: No dummy data generated in production environment
- **Comprehensive**: Includes all entity types with realistic relationships

## Configuration

### Environment Variables

| Variable | Description | Default | Examples |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | `development` | `development`, `production` |
| `DATABASE_URL` | Custom database URL | *(auto-generated)* | `sqlite:///custom.sqlite` |
| `LOG_LEVEL` | Application log level | `INFO` | `DEBUG`, `INFO`, `WARNING` |

### Setting the Environment

#### Development (Default)
```bash
# No configuration needed - defaults to development
python -m uvicorn src.main:app --reload
```

#### Production
```bash
export ENVIRONMENT=production
python -m uvicorn src.main:app
```

#### Custom Database
```bash
export DATABASE_URL=sqlite:///my_custom.sqlite
python -m uvicorn src.main:app
```

## Database Management

### Initial Setup

1. **Run Migrations**: 
   ```bash
   # Development database
   alembic upgrade head
   
   # Production database  
   ENVIRONMENT=production alembic upgrade head
   ```

2. **Generate Dummy Data** (development only):
   ```bash
   # Automatic - runs on application startup in development
   # Or manually:
   python generate_dummy_data.py
   ```

### Database Files

- `tap_dev.sqlite` - Development database with dummy data
- `tap_prod.sqlite` - Production database (clean)
- `tap.sqlite` - Legacy database (if exists)

## Dummy Data Generated

The development environment includes the following sample data:

### 👥 Organizations & Employees
- **Org Units**: Engineering, Sales, Marketing
- **Employees**: John Doe (Manager), Jane Smith (Employee)
- **Users**: Both employees have login credentials (password: `password123`)

### 🔐 Authentication & Authorization
- **Auth Roles**: Employee, Manager
- **Permissions**: Appropriate permissions for each role
- **Memberships**: Users assigned to roles

### 🏢 Departments
- **Departments**: Backend Development, Sales Team
- **Memberships**: Employees assigned to departments

### 📅 Time Management
- **Holiday Groups**: US Holidays
- **Holidays**: New Year's Day, Independence Day
- **Timeclock**: Sample clock-in entries

## Usage Examples

### Checking Current Configuration
```python
from src.config import Settings

settings = Settings()
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Database: {settings.get_database_url()}")
```

### Querying Development Data
```python
from src.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # List all employees
    result = conn.execute(text("""
        SELECT badge_number, first_name, last_name 
        FROM employees WHERE id > 0
    """))
    for row in result:
        print(f"{row.badge_number}: {row.first_name} {row.last_name}")
```

### Testing Login Credentials
Development users can log in with:
- **Username**: `EMP001` or `EMP002`
- **Password**: `password123`

## Files Modified

| File | Changes |
|------|---------|
| `src/config.py` | Added database URL configuration and environment detection |
| `src/database.py` | Modified to use environment-aware database URLs |
| `src/services.py` | Added dummy data generation function |
| `src/main.py` | Added call to generate dummy data on startup |
| `alembic.ini` | Updated to support environment-based configuration |
| `alembic/env.py` | Modified to use settings-based database URL |

## Testing

### Comprehensive Test Suite
Run the full test suite to validate functionality:
```bash
# Run all tests (from /tmp/comprehensive_test.py)
python /tmp/comprehensive_test.py
```

### Manual Testing
```bash
# Test development environment
ENVIRONMENT=development python generate_dummy_data.py

# Test production environment (should skip dummy data)
ENVIRONMENT=production python generate_dummy_data.py

# Test custom database
DATABASE_URL=sqlite:///test.sqlite python generate_dummy_data.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Locked**: Close any SQLite browser connections
3. **Migration Errors**: Run `alembic upgrade head` with correct environment

### Verification Commands
```bash
# Check database files exist
ls -la *.sqlite

# Verify table structure
sqlite3 tap_dev.sqlite ".tables"

# Count records in development database
sqlite3 tap_dev.sqlite "SELECT COUNT(*) FROM employees WHERE id > 0;"
```

## Migration from Legacy Setup

If migrating from the previous single-database setup:

1. **Backup existing data**: `cp tap.sqlite tap_backup.sqlite`
2. **Run migrations**: `alembic upgrade head` (creates `tap_dev.sqlite`)
3. **Migrate data**: Copy important data from `tap.sqlite` to appropriate environment database
4. **Test thoroughly**: Verify application works with new configuration

## Security Considerations

- **Production databases** contain no dummy data or test credentials
- **Development passwords** are clearly marked as test-only
- **Database files** should be properly secured in production deployments
- **Environment variables** should be set securely in production

## Future Enhancements

- Support for PostgreSQL/MySQL in production
- Environment-specific logging configurations  
- Automated backup strategies per environment
- Docker-based environment management