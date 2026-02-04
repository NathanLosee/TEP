# TAP (Timeclock and payroll) - Copilot Developer Guide

## Repository Overview

**TAP** is a full-stack employee management system providing timeclock functionality, authentication/authorization, and payroll features. The application consists of a FastAPI Python backend with an Angular frontend, designed for managing employees, departments, schedules, and time tracking.

**Key Statistics:**
- **Type**: Full-stack web application (REST API + SPA)
- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Frontend**: Angular 19 with TypeScript and Angular Material
- **Database**: SQLite with environment-specific databases (development/production)
- **Size**: ~15 domain modules, comprehensive test suite
- **Architecture**: Domain-driven design with modular organization

## Quick Start & Build Instructions

### Critical Prerequisites
⚠️ **IMPORTANT**: This project requires **Python 3.11+** due to modern syntax usage (union types). The GitHub Actions currently use Python 3.9 which causes syntax errors. If you encounter `TypeError: unsupported operand type(s) for |`, you need Python 3.11+.

### Backend Setup (Always Required)
```bash
# 1. Install dependencies - ALWAYS run this first
pip install -r requirements.txt

# 2. Additional dependencies not in requirements.txt (REQUIRED)
pip install alembic bcrypt pyjwt flake8 pytest pytest-cov

# 3. Set up environment variables (create .env file in root)
LOG_LEVEL=INFO
ENVIRONMENT=development
# DATABASE_URL is optional - auto-generated based on ENVIRONMENT

# 4. Run database migrations - ALWAYS required before starting app
alembic upgrade head

# 5. Start the backend server
uvicorn src.main:app --reload
# Server runs on http://127.0.0.1:8000
# API docs available at http://127.0.0.1:8000/docs
```

### Frontend Setup (If Modifying Frontend)
```bash
cd frontend

# Install dependencies
npm ci  # Use npm ci for faster, reliable installs

# Development server
npm run start    # or ng serve
# Runs on http://localhost:4200

# Build for production  
npm run build    # or ng build

# Run tests
npm run test     # or ng test
```

### Testing
```bash
# Backend tests (from repository root)
pytest tests                                    # All tests
pytest tests/integration                        # Integration tests only
pytest tests --cov=src --cov-report=html       # With coverage report

# Frontend tests (from frontend/ directory)
cd frontend
npm run test      # Unit tests with Karma/Jasmine
npm run e2e       # End-to-end tests with Playwright
```

### Linting & Validation
```bash
# Python linting (backend)
flake8 src                    # Lint source code

# Security scanning
bandit -r src                 # Security vulnerability scanning
safety check                  # Dependency vulnerability checking

# Frontend linting (from frontend/ directory)
cd frontend
npm run lint                  # ESLint checking
```

## Environment Configuration

### Database Behavior
- **Development** (`ENVIRONMENT=development`): Uses `tap_dev.sqlite`, automatically generates dummy data
- **Production** (`ENVIRONMENT=production`): Uses `tap_prod.sqlite`, no dummy data
- **Test** (`ENVIRONMENT=test`): Uses `tap_test.sqlite` for testing
- **Custom**: Set `DATABASE_URL` directly to override

### Common Commands by Environment
```bash
# Development (default)
alembic upgrade head
uvicorn src.main:app --reload

# Production
ENVIRONMENT=production alembic upgrade head
ENVIRONMENT=production uvicorn src.main:app

# Testing
pytest tests  # Uses test database automatically
```

## Project Architecture & File Layout

### Backend Structure (`/src/`)
```
src/
├── main.py                 # FastAPI app entry point, router imports, middleware
├── config.py              # Settings & environment configuration
├── database.py            # SQLAlchemy setup & session management  
├── services.py            # Cross-domain services (auth, dummy data)
├── constants.py           # Application-wide constants
├── logger/                # Logging configuration & formatters
├── auth_role/             # Authentication & authorization (JWT, roles)
├── employee/              # Employee management & profiles
├── user/                  # User accounts & authentication
├── department/            # Department organization & memberships
├── org_unit/              # Organizational unit hierarchy
├── holiday_group/         # Holiday calendars & time-off management
├── timeclock/             # Time tracking & clock in/out
└── event_log/             # System event logging & audit trails
```

### Frontend Structure (`/frontend/`)
```
frontend/
├── src/
│   ├── app/               # Angular application modules & routing
│   ├── interceptors/      # HTTP interceptors for API communication
│   └── environments/      # Environment-specific configurations
├── angular.json           # Angular CLI configuration
├── package.json           # Dependencies & npm scripts
└── playwright.config.ts   # E2E testing configuration
```

### Key Configuration Files
- `pyproject.toml` - Python project metadata (Poetry format but uses pip)
- `requirements.txt` - Python dependencies (MISSING: alembic, bcrypt, pyjwt, flake8, pytest, pytest-cov)
- `alembic.ini` - Database migration configuration
- `alembic/env.py` - Migration environment setup
- `.github/workflows/copilot-setup-staps.yml` - CI setup (uses Python 3.9 - OUTDATED)

## Domain Model & Database

### Core Entities
- **Employee**: Badge number, personal info, payroll settings, organizational assignment
- **User**: Login credentials, linked to Employee
- **AuthRole**: Role-based permissions (Employee, Manager, Admin)
- **Department**: Organizational groupings with employee memberships
- **OrgUnit**: Hierarchical organizational structure
- **HolidayGroup**: Holiday calendars assignable to employees
- **Timeclock**: Clock in/out entries with timestamp tracking
- **EventLog**: System audit trail

### Key Relationships
- Employee ←→ User (1:1, badge_number links)
- Employee → OrgUnit (many:1)
- Employee → HolidayGroup (many:1, optional)
- Employee → Department (many:many via memberships)
- User → AuthRole (many:many via memberships)

## Common Issues & Solutions

### Build Failures
1. **"unsupported operand type(s) for |"** - Python version < 3.11
   - Solution: Use Python 3.11+ or modify union syntax to `Union[Type, None]`
2. **"No module named 'bcrypt'"** - Missing dependencies
   - Solution: `pip install alembic bcrypt pyjwt`
3. **"alembic: command not found"** - Alembic not in PATH
   - Solution: Use full path or ensure proper installation

### Database Issues
1. **Migration failures** - Missing database or permissions
   - Solution: Check database file permissions, run `alembic upgrade head`
2. **Empty database** - Migrations not applied
   - Solution: Always run `alembic upgrade head` before starting app

### Frontend Issues
1. **Dependencies not found** - node_modules missing
   - Solution: Run `npm ci` in frontend/ directory
2. **Build failures** - Outdated Angular CLI
   - Solution: Use npm scripts instead of global ng command
3. **Build budget warnings** - Bundle size exceeds configured limits
   - Note: Warnings are expected due to large Material UI components, build still succeeds

## Testing Strategy

### Backend Testing
- **Integration Tests**: Full API testing with test database (`tests/integration/`)
- **Test Data**: Automated fixtures and factories in `conftest.py`
- **Authentication**: Test utilities for user login and authorization
- **Coverage**: Use `--cov=src --cov-report=html` for detailed coverage reports

### Frontend Testing  
- **Unit Tests**: Component testing with Karma/Jasmine
- **E2E Tests**: Full application testing with Playwright
- **Mock Data**: Test services and HTTP interceptors for API mocking

## Development Workflow

### Making Changes
1. **Backend Changes**:
   - Modify source in `/src/` following domain organization
   - Run `flake8 src` for linting
   - Add/update tests in `/tests/`
   - Test with `pytest tests`

2. **Database Changes**:
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Review generated migration file
   - Apply: `alembic upgrade head`

3. **Frontend Changes**:
   - Work in `/frontend/src/`
   - Follow Angular style guide
   - Test with `npm run test` and `npm run e2e`

### Validation Checklist
- [ ] Backend starts without errors (`uvicorn src.main:app --reload`)
- [ ] Database migrations apply successfully (`alembic upgrade head`)
- [ ] Tests pass (`pytest tests`)
- [ ] Linting passes (`flake8 src`)
- [ ] Frontend builds (`npm run build`)
- [ ] API documentation accessible at `/docs`

## Security & Authentication

### JWT Authentication
- Login endpoint: `POST /users/login`
- Protected routes require `Authorization: Bearer <token>` header
- Roles: Employee, Manager, Admin with granular permissions
- Default test credentials: `badge_number: "0", password: "password123"`

### Development vs Production
- **Development**: Includes dummy users with test passwords
- **Production**: Clean database, secure configuration required
- **Testing**: Isolated test database with fixtures

## Performance Considerations

### Database
- SQLite suitable for development/small deployments
- Consider PostgreSQL for production with high concurrency
- Database migrations can be slow with large datasets

### Frontend
- Angular build optimizations enabled by default
- Lazy loading configured for large feature modules
- HTTP interceptors handle authentication and error scenarios

---

**Trust these instructions**: This guide is comprehensive and tested. Only search for additional information if these instructions are incomplete or found to be incorrect for your specific use case.