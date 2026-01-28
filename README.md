# TEP - Timeclock and Employee Payroll

REST API and web application for employee timeclock management and payroll processing. Supports employee clocking in/out, report generation, organizational structure management, and comprehensive administrative features.

## Features

- **Employee Timeclock**: Clock in/out functionality with browser-based device registration
- **Payroll Reports**: Generate detailed payroll reports with overtime and holiday calculations
- **Employee Management**: Manage employee records, departments, and organizational units
- **Role-Based Access Control**: Granular permissions system with customizable auth roles
- **License Management**: Ed25519 cryptographic license activation for admin features
- **Event Logging**: Comprehensive audit trail for all system operations
- **Holiday Groups**: Configurable holiday calendars with recurring holiday support
- **Registered Browsers**: Secure browser registration system for controlled timeclock access

## Technology Stack

### Backend
- **Python 3.13+** with Poetry dependency management
- **FastAPI** web framework
- **SQLAlchemy** ORM with Alembic migrations
- **SQLite** database (development)
- **JWT** authentication with RSA-256
- **Ed25519** cryptographic signatures for license verification

### Frontend
- **Angular 19+** standalone components
- **Angular Material** (Material Design 3)
- **TypeScript** with RxJS for reactive programming
- **Jasmine/Karma** for testing

## Prerequisites

### Backend Requirements
- **Python 3.13+**: Check version with `python --version`
  - Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Poetry 1.6+**: Check version with `poetry --version`
  - Install: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

### Frontend Requirements
- **Node.js 18+** and **npm 9+**: Check with `node --version` and `npm --version`
  - Download: [https://nodejs.org/](https://nodejs.org/)

## Setup Instructions

### Backend Setup

1. **Create virtual environment and install dependencies**
   ```bash
   poetry install
   ```

2. **Set up environment variables** (optional)

   Create a `.env` file in the root directory:
   ```text
   LOG_LEVEL=INFO
   ENVIRONMENT=development
   CORS_ORIGINS=http://localhost:4200
   ROOT_PASSWORD=your_secure_password_here
   ```

3. **Activate virtual environment**
   ```bash
   poetry shell
   ```

4. **Run database migrations**
   ```bash
   poetry run alembic upgrade head
   ```

5. **Generate RSA key pair for JWT authentication**

   The application will automatically generate keys on first run if they don't exist.

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment** (if needed)

   Edit `frontend/src/environments/environment.development.ts`:
   ```typescript
   export const environment = {
     production: false,
     apiUrl: 'http://localhost:8000',
   };
   ```

## Running the Application

### Start Backend Server

From the root directory:
```bash
poetry run uvicorn src.main:app --reload
```

The API will be available at:
- **API**: http://127.0.0.1:8000
- **Swagger Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Start Frontend Development Server

From the `frontend/` directory:
```bash
npm start
```

The application will be available at:
- **Web App**: http://localhost:4200

### Default Credentials

**Root User (Development)**
- **Badge Number**: `0`
- **Password**: Auto-generated on first run (printed to console) or value of `ROOT_PASSWORD` env var

**Important**:
- In production, `ROOT_PASSWORD` environment variable **must** be set
- In development, if not set, a secure random password is generated and displayed in the console

## Testing

### Backend Testing

Run all tests:
```bash
poetry run pytest tests/
```

Run only integration tests:
```bash
poetry run pytest tests/integration/
```

Run only unit tests:
```bash
poetry run pytest tests/unit/
```

Run with coverage report:
```bash
poetry run pytest tests/ --cov=src --cov-report=html:cov_html --cov-report=term-missing
```

### Frontend Testing

From the `frontend/` directory:

Run tests in watch mode:
```bash
npm test
```

Run tests once:
```bash
npm test -- --watch=false --browsers=ChromeHeadless
```

## Project Structure

```
TEP/
├── src/                          # Backend source code
│   ├── auth_role/               # Role-based access control
│   ├── department/              # Department management
│   ├── employee/                # Employee records
│   ├── event_log/               # Audit logging
│   ├── holiday_group/           # Holiday calendar management
│   ├── license/                 # License activation/verification
│   ├── org_unit/                # Organizational units
│   ├── registered_browser/      # Browser registration for timeclock
│   ├── report/                  # Payroll report generation
│   ├── system_settings/         # Application settings (theme, logo)
│   ├── timeclock/               # Clock in/out operations
│   ├── user/                    # User authentication
│   ├── config.py               # Application configuration
│   ├── constants.py            # Global constants
│   ├── database.py             # Database connection
│   ├── main.py                 # FastAPI application entry point
│   └── services.py             # Shared service functions
├── frontend/                    # Angular frontend application
│   ├── src/
│   │   ├── app/                # Angular components
│   │   ├── services/           # API client services
│   │   └── styles/             # Global styles
├── tests/                       # Backend tests
│   ├── integration/            # API integration tests
│   └── unit/                   # Unit tests
├── scripts/                     # Utility scripts
│   ├── build_release.py        # Production build script
│   ├── init_database.py        # Database initialization
│   ├── backup_database.py      # Database backup utility
│   └── restore_database.py     # Database restore utility
├── tools/                       # Development/admin tools
│   └── license_generator.py    # License key generation
├── installer/                   # NSIS Windows installer
│   ├── tep-installer.nsi       # NSIS installer script
│   └── favicon.ico             # Installer icon
├── alembic/                    # Database migrations
├── run_server.py               # Server entry point (for PyInstaller)
├── tep.spec                    # PyInstaller build specification
├── pyproject.toml              # Poetry dependencies
├── .env.example                # Environment configuration template
├── README.md                   # This file
└── DEPLOYMENT.md               # Production deployment guide
```

## API Overview

### Core Modules

- **Authentication** (`/users/login`, `/users/logout`)
  - JWT-based authentication with refresh tokens
  - Password change functionality

- **Timeclock** (`/timeclock/{badge_number}`)
  - Clock in/out operations
  - Timeclock status checking
  - Entry management

- **Employees** (`/employees`)
  - CRUD operations for employee records
  - Search and filtering
  - Department and org unit associations

- **Reports** (`/reports`)
  - Payroll report generation
  - PDF export functionality
  - Filtering by employee, department, org unit, date range

- **Admin Features** (require valid license)
  - Auth role management
  - Department management
  - Organizational unit management
  - Holiday group management
  - Registered browser management
  - Event log viewing

### License System

The application uses a **cryptographic license system** to control access to administrative features:

- **License Format**: Ed25519 cryptographic signatures (128-character hex strings)
- **Activation**: Offline activation via admin interface
- **Scope**: Admin features are locked without valid license; timeclock functionality remains available
- **License Status**: Publicly accessible at `/licenses/status` (no authentication required)

To activate a license:
1. Log in as an administrator
2. Navigate to License Management
3. Enter the license key
4. Click "Activate License"

## Production Build

### Building a Release Package

The project includes a build script that creates a production-ready release package.

**Source Distribution** (requires Python on target):
```bash
python scripts/build_release.py --version 1.0.0
```

**Standalone Executable** (PyInstaller, no Python required):
```bash
python scripts/build_release.py --version 1.0.0 --executable
```

**Windows Installer** (NSIS, includes executable):
```bash
python scripts/build_release.py --version 1.0.0 --executable --installer
```

**Quick Build** (skip tests):
```bash
python scripts/build_release.py --version 1.0.0 --executable --skip-tests
```

### Build Output

The build creates:
- `build/TEP-{version}/` - Complete release package
- `releases/TEP-{version}.zip` - Distribution archive
- `releases/TEP-Setup-{version}.exe` - Windows installer (with `--installer` flag)

Package contents:
- `backend/` - Backend executable or source code
- `frontend/` - Angular production build
- `config/` - Configuration templates (.env.example)
- `scripts/` - Utility scripts (backup, restore, license generator)
- `docs/` - Documentation

### Running the Executable

```bash
# Navigate to backend directory
cd build/TEP-1.0.0/backend

# Set environment (Windows)
set ENVIRONMENT=production
set ROOT_PASSWORD=YourSecurePassword123

# Run server
tep.exe
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Development

### Database Migrations

Create a new migration:
```bash
poetry run alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```

Rollback one migration:
```bash
poetry run alembic downgrade -1
```

### Code Quality

The project uses:
- **Black** for Python code formatting
- **Flake8** for Python linting
- **ESLint** for TypeScript linting
- **Prettier** for TypeScript formatting

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ENVIRONMENT` | `development` | Environment mode (development, production, test) |
| `CORS_ORIGINS` | `http://localhost:4200` | Allowed CORS origins (comma-separated) |
| `ROOT_PASSWORD` | *(required in production)* | Root user password (auto-generated in dev if not set) |
| `DATABASE_URL` | `sqlite:///tep.sqlite` | Database connection string |
| `JWT_KEY_PASSWORD` | *(optional)* | Password to encrypt JWT RSA private key |
| `BACKEND_PORT` | `8000` | Backend server port |

## Security Considerations

1. **Change default root password** in production environments
2. **Configure CORS origins** appropriately for your deployment
3. **Use HTTPS** in production
4. **Secure license keys** - private keys must never be embedded in the application
5. **Regular backups** of the SQLite database

## Troubleshooting

### Backend won't start
- Verify Python version: `python --version` (must be 3.13+)
- Ensure dependencies installed: `poetry install`
- Check database migrations: `poetry run alembic upgrade head`

### Frontend won't compile
- Verify Node.js version: `node --version` (must be 18+)
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

### Tests failing
- Ensure test database is clean
- Check for port conflicts (8000 for backend, 4200 for frontend)
- Run tests in isolation: `poetry run pytest tests/integration/test_specific.py`

## License

Copyright © 2024-2026. All Rights Reserved.

Proprietary and confidential.
