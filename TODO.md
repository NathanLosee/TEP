# TEP - Project TODO List

This document tracks planned improvements, bug fixes, and enhancements for the TEP (Timeclock and Employee Payroll) project.

---

## High Priority

### Security & Reliability

- [x] **Improve Root Password Security** ✅ (Completed)
  - ~~**Issue**: Default root password is "password" if `ROOT_PASSWORD` env var not set~~
  - **File**: `src/services.py:119-129`
  - **Solution**: Fails in production if ROOT_PASSWORD not set, generates random password in dev/test
  - **Priority**: HIGH - Security vulnerability

- [x] **Add Database Session Error Handling** ✅ (Completed)
  - ~~**Issue**: No exception handling in `db.close()` within finally block~~
  - **File**: `src/database.py:50-56`
  - **Solution**: Try-except block added in finally to prevent exception propagation
  - **Priority**: HIGH - Reliability

### Terminology & Consistency

- [x] **Standardize Device/Browser Terminology** ✅ (Completed)
  - ~~**Issue**: Backend uses "browser", frontend mixes "device" and "browser"~~
  - **Files Updated**:
    - Frontend: `frontend/src/services/browser-uuid.service.ts` (renamed from device-uuid)
    - Frontend: `frontend/src/services/registered-browser.service.ts` (renamed from registered-device)
    - Frontend: `frontend/src/app/registered-browser-management/` (renamed from registered-device-management)
    - Event logs: Updated to use "browser" terminology
  - **Result**: All references now consistently use "browser"
  - **Priority**: HIGH - Developer experience

- [x] **Standardize Import Organization** ✅ (Completed)
  - ~~**Issue**: Mix of relative and absolute imports across codebase~~
  - **Solution**: Changed all route files to use direct `from` imports with aliases for repository functions
  - **Files Updated**: All route files (auth_role, user, employee, department, org_unit, holiday_group, timeclock, registered_browser, license, event_log)
  - **Key Changes**:
    - Removed route-to-route imports (which caused circular dependencies) and replaced with repository imports
    - Fixed naming conflicts where route functions shadowed imported repository functions (caused infinite recursion)
    - Pattern: Import repository functions with `_from_db` or `_in_db` suffix, keep route function names clean
  - **Priority**: MEDIUM - Code consistency

---

## Medium Priority

### Architecture & Design

- [x] **Document and Standardize License Enforcement Strategy** ✅ (Completed)
  - **Strategy Implemented**:
    - **No license required**: READ operations (GET), public endpoints (login, logout, refresh, license management, browser verify/recover, system settings/logo GET)
    - **License required**: WRITE operations (POST, PUT, DELETE) on all admin data, plus timeclock punch-in/out and report generation
  - **Files Updated**: All route files (auth_role, department, org_unit, holiday_group, employee, user, registered_browser, event_log, timeclock, system_settings, report)
  - **Benefit**: Users can evaluate the system (view data), but modifications and core operations require a valid license
  - **Priority**: MEDIUM - Feature clarity

- [x] **Fix Race Condition in Browser Registration** ✅ (Completed)
  - ~~**Issue**: Check-then-act pattern without transaction lock~~
  - **File**: `src/registered_browser/routes.py`
  - **Solution**: Removed pre-checks, rely on database unique constraint + catch `IntegrityError`
  - **Priority**: MEDIUM - Data integrity

### Testing

- [ ] **Increase Unit Test Coverage to 70%+**
  - **Current**: Mostly integration tests, limited unit tests
  - **Needed**:
    - Unit tests for `src/license/key_generator.py`
    - Unit tests for service functions in `src/services.py`
    - Frontend unit tests for license service
    - Frontend unit tests for permission service
  - **Priority**: MEDIUM - Code quality

- [ ] **Add Tests for Race Conditions**
  - **Area**: Browser registration, license activation
  - **Priority**: MEDIUM - Reliability

---

## Low Priority

### Performance Optimizations

- [x] **Add Database Indexes** ✅ (Completed)
  - **Indexes Added**:
    - `licenses.is_active` - for license status checks
    - `timeclock_entries.clock_in` - for date range queries
    - `timeclock_entries.badge_number` - for employee filtering
    - `registered_browsers.fingerprint_hash` - for fingerprint lookups
    - `registered_browsers.last_seen` - for session cleanup queries
  - **Migration**: `e5f6a7b8c9d0_add_performance_indexes.py`
  - **Priority**: LOW - Performance

- [x] **Prevent N+1 Query Issues** ✅ (Completed)
  - **Fixed in `src/employee/repository.py`**:
    - `get_employees()` - Added `selectinload()` for org_unit, holiday_group, departments
    - `search_for_employees()` - Added `selectinload()` for org_unit, holiday_group, departments
  - Timeclock queries already use JOINs (no N+1 issue)
  - **Priority**: LOW - Performance

- [ ] **Add Frontend Caching**
  - **Current**: Permission and license status checked on every app init
  - **Solution**: Cache in localStorage with TTL, refresh only on demand
  - **Files**: `frontend/src/services/license.service.ts`, `frontend/src/services/permission.service.ts`
  - **Priority**: LOW - Performance

### Code Quality

- [ ] **Consider TypeScript Interface Naming Convention**
  - **Current**: Uses snake_case (consistent with backend)
  - **Observation**: camelCase is more idiomatic for TypeScript
  - **Decision Needed**: Keep snake_case for consistency or switch to camelCase
  - **Priority**: LOW - Style preference

- [ ] **Enhanced Error Response Format**
  - **Current**: Simple error strings
  - **Enhancement**: Include field context in error responses
  - **Example**:
    ```json
    {
      "detail": "Badge number already exists",
      "field": "badge_number",
      "value": "EMP001",
      "constraint": "unique"
    }
    ```
  - **Priority**: LOW - Developer experience

- [x] **Scheduled Cleanup for Stale Browser Sessions** ✅ (Completed)
  - **Implementation**: Background task using FastAPI lifespan context manager
  - **Files Created/Modified**:
    - `src/scheduler.py` - New module with `periodic_cleanup()` task (runs every 5 minutes)
    - `src/main.py` - Added lifespan handler to start/stop scheduler
  - **Note**: Direct calls in verify/recover endpoints kept as immediate fallback
  - **Priority**: LOW - Architecture improvement

### Validation

- [x] **Add Badge Number Format Validation** ✅ (Completed)
  - **Pattern**: `^[A-Za-z0-9][A-Za-z0-9_-]{0,19}$` (alphanumeric, dashes, underscores, 1-20 chars)
  - **Files Updated**:
    - `src/constants.py` - Added `BADGE_NUMBER_REGEX` and `EXC_MSG_INVALID_BADGE_FORMAT`
    - `src/employee/schemas.py` - Added pattern validation to `badge_number` field
    - `src/user/schemas.py` - Added pattern validation to `badge_number` fields
  - **Priority**: LOW - Data quality

- [x] **~~Add Server ID Format Validation~~** ✅ (No longer applicable)
  - **Reason**: The `server_id` field was removed in migration `d4e5f6a7b8c9`. Machine binding is now handled via the `activation_key` signed by the license server.

---

## Feature Enhancements

### UI/UX Improvements

- [x] **Make Material Design Theme Configurable via System Settings** ✅ (Completed)
  - **Implementation**:
    - Theme colors (primary, secondary, accent/tertiary) configurable via System Settings UI
    - Logo uploadable via System Settings (stored in database)
    - `SystemSettingsService.applyTheme()` dynamically applies CSS variables
    - Default colors match Angular Material M3 theme (`#02E600`, `#BBCBB2`, `#CDCD00`)
    - When using defaults, SCSS theme is preserved; custom colors generate tonal palette
  - **Files Modified**:
    - `frontend/src/services/system-settings.service.ts`
    - `frontend/src/app/system-settings/` (UI components)
    - `src/system_settings/` (backend API and models)
  - **Priority**: LOW - Customization
  - **Benefit**: Easy theme customization without code changes

- [x] **Enhance PDF Report Appearance** ✅ (Completed)
  - **Implemented Features**:
    1. **Logo Integration**:
       - Large semi-transparent watermark (6 inches) centered on each page
       - Uses logo from System Settings (stored in database)
    2. **Layout Improvements**:
       - Employee summary and details kept together on same page (`KeepTogether`)
       - Skip general summary for single-employee reports (avoids empty section)
       - Department/Org Unit name displayed in header when applicable
    3. **Styling Enhancements**:
       - Colored headers with proper typography
       - Table styling with borders and background colors
       - Monthly breakdown with totals
    4. **Additional Elements**:
       - Report generation date/time in header
       - Company name in header (from System Settings)
       - Report period displayed
  - **Files Modified**:
    - `src/report/pdf_export.py` - PDF generation with watermark and styling
    - `src/report/service.py` - Added filter_name for dept/org unit
    - `src/report/schemas.py` - Added filter_name to ReportResponse
  - **Priority**: LOW - Polish
  - **Benefit**: More professional-looking reports for clients/management

- [ ] **Expose Password Change Feature in UI**
  - **Status**: Backend endpoint exists, but not in frontend navigation
  - **Files**:
    - Backend: `src/user/routes.py` (endpoint exists)
    - Frontend: Missing component in navigation
  - **Solution**: Add password change link in user menu/profile
  - **Priority**: LOW - Feature completion

### New Features

- [ ] **Offline Support for Timeclock**
  - **Current**: Always requires backend connection
  - **Enhancement**: Implement offline queue for timeclock entries
  - **Benefit**: Employees can still clock in/out during network outages
  - **Priority**: LOW - Nice to have

- [ ] **Enhanced Audit Trail for License Operations**
  - **Current**: Event logging exists but minimal details
  - **Enhancement**: Log license key changes with before/after values
  - **Priority**: LOW - Audit improvement

- [ ] **Observability Improvements**
  - **Enhancements**:
    - Better structured logging
    - Metrics collection (response times, error rates)
    - Health check endpoint
  - **Priority**: LOW - Operations

---

## Documentation

- [x] **Rewrite README.md** ✅ (Completed)
  - ~~Old README referenced "Super Health API" instead of TEP~~
  - ~~Created comprehensive TEP-specific documentation~~

- [ ] **Add API Documentation Examples**
  - **Enhancement**: Add request/response examples to Swagger docs
  - **Files**: Add examples to route docstrings
  - **Priority**: LOW - Documentation

- [x] **Create Deployment Guide** ✅ (Completed)
  - **File**: `DEPLOYMENT.md`
  - **Topics Covered**:
    - Production environment setup
    - Environment variable configuration
    - Database backup strategies
    - SSL/HTTPS setup recommendations
    - CORS configuration for production
    - Windows service management
    - Troubleshooting guide
  - **Priority**: LOW - Documentation

---

## Packaging & Deployment

### Production Packaging

- [x] **Create Production Build Scripts** ✅ (Completed)
  - **Implementation**:
    - `scripts/build_release.py` - Complete release packager with:
      - Prerequisite checking (poetry, node, npm, pyinstaller)
      - Backend + frontend test execution
      - Frontend production build (Angular AOT compilation)
      - Backend packaging (source mode or PyInstaller executable)
      - Database structure and migrations
      - Configuration templates
      - Documentation bundling
      - ZIP archive creation
    - `tep.spec` - PyInstaller spec file for Windows executable
    - `run_server.py` - Entry point for uvicorn server
  - **Usage**:
    - Source mode: `python scripts/build_release.py --version 1.0.0`
    - Executable mode: `python scripts/build_release.py --version 1.0.0 --executable`
  - **Priority**: HIGH - Required for distribution

- [x] **Create Installation Package** ✅ (Completed)
  - **Type**: Windows installer (.exe) using NSIS
  - **Files**:
    - `installer/tep-installer.nsi` - NSIS installer script
    - `installer/favicon.ico` - Installer icon
    - `LICENSE` - License agreement shown during install
  - **Installer Features**:
    - Custom installation directory selection
    - Configuration page for root password and port
    - Desktop shortcut creation
    - Start menu entries with Open TEP, Documentation, Uninstall
    - Windows Firewall rule configuration
    - Start/Stop batch scripts
    - Uninstaller with option to keep data
  - **Usage**:
    - `python scripts/build_release.py --version 1.0.0 --executable --installer`
    - Or standalone: `makensis /DVERSION=1.0.0 installer/tep-installer.nsi`
  - **Priority**: HIGH - Required for distribution

- [x] **Create Deployment Documentation** ✅ (Completed)
  - **File**: `DEPLOYMENT.md`
  - **Topics Covered**:
    - System requirements
    - Installation methods (Windows installer, PyInstaller executable, manual)
    - Environment variable configuration
    - Database initialization and management
    - Backup/restore procedures
    - License activation
    - Service management (standalone and Windows service via NSSM)
    - Troubleshooting
    - Security best practices
  - **Priority**: HIGH - Required for distribution

- [x] **Backend Service Configuration** ✅ (Completed)
  - **Implementation**: PowerShell script using NSSM for Windows service management
  - **Files**:
    - `scripts/install-service.ps1` - Automated NSSM download and service installation
  - **Features**:
    - Auto-downloads NSSM if not present
    - Configures service with auto-start on boot
    - Log rotation for stdout/stderr
    - Automatic restart on failure
    - Interactive prompts for starting service
  - **Installer Integration**:
    - NSIS installer includes `install-service.bat` and `uninstall-service.bat`
    - Uninstaller automatically removes Windows service
  - **Usage**:
    - `.\scripts\install-service.ps1` - Install as service
    - `.\scripts\install-service.ps1 -Uninstall` - Remove service
  - **Priority**: HIGH - Production requirement

- [x] **Configuration Management** ✅ (Completed)
  - **Implementation**:
    - `.env.example` template file created with documented configuration options
    - Installer prompts for root password and backend port
    - Installer auto-generates secure random JWT_KEY_PASSWORD (32-byte base64)
    - RSA keys are generated on first run (existing `load_keys()` function)
    - JWT key encryption supported via JWT_KEY_PASSWORD environment variable
  - **Files**:
    - `.env.example` - Configuration template with all options documented
    - `installer/tep-installer.nsi` - NSIS installer with key generation
    - `src/services.py` - RSA key generation and encryption
  - **Priority**: HIGH - Production requirement

- [x] **Frontend Web Server Setup** ✅ (Completed)
  - **Implementation**: Frontend served directly from FastAPI in production mode
  - **Features**:
    - Static file serving for Angular assets (JS, CSS, images)
    - Client-side routing support (returns index.html for Angular routes)
    - Single-server deployment (no separate web server needed)
    - Automatic frontend detection from `../frontend` relative to executable
  - **Files Modified**:
    - `src/main.py` - Added `setup_static_files()` for production mode
    - `src/config.py` - Handle PyInstaller .env file path
    - `run_server.py` - Load .env early, database auto-initialization
  - **Priority**: HIGH - Production requirement

- [x] **Database Bundling** ✅ (Completed)
  - **Implementation**:
    - `scripts/init_database.py` - Initialize database with Alembic migrations
    - `scripts/backup_database.py` - Timestamped backups with optional gzip compression
    - `scripts/restore_database.py` - Restore with safety backup and integrity verification
  - **Features**:
    - Schema verification after initialization
    - Automatic old backup cleanup (configurable retention)
    - Safety backup before restore operations
  - **Priority**: HIGH - Production requirement

- [x] **License Key Generator Tool** ✅ (Completed)
  - **Implementation**: `tools/license_generator.py`
  - **Features**:
    - Generate Ed25519 key pair (`--generate-keypair`)
    - Generate signed license keys (`--generate-license --private-key FILE`)
    - Verify license keys (`--verify-license KEY --public-key FILE`)
    - Batch key generation (`--count N`)
  - **Security**: Private key stored separately, not distributed with application
  - **Priority**: HIGH - Required for licensing

- [ ] **Update Mechanism**
  - **Features**:
    - Check for updates
    - Download and apply updates
    - Database migration during updates
    - Rollback capability
  - **Priority**: MEDIUM - Future enhancement

### Release Checklist

- [ ] **Pre-Release Checklist**
  - [ ] All tests passing (backend + frontend)
  - [ ] Security audit completed
  - [ ] Default passwords changed/removed
  - [ ] CORS configured for production
  - [ ] Error messages reviewed (no sensitive info)
  - [ ] Logging configured appropriately
  - [ ] Performance testing completed
  - [ ] Documentation up to date
  - [ ] License generator ready
  - [ ] Sample license keys generated for testing

- [ ] **Build Process**
  1. [ ] Bump version numbers
  2. [ ] Run all tests
  3. [ ] Build backend executable
  4. [ ] Build frontend production bundle
  5. [ ] Package database and migrations
  6. [ ] Create installer
  7. [ ] Test installation on clean Windows machine
  8. [ ] Generate release notes
  9. [ ] Create distribution package
  10. [ ] Archive for distribution

---

## Completed ✅

- [x] **Fix README.md** - Was referencing "Super Health API" instead of TEP
- [x] **Move Hardcoded Error Messages to Constants** - Timeclock routes cleaned up
- [x] **Implement License System** - Ed25519 cryptographic license activation
- [x] **Add Comprehensive Testing** - 249 backend + 343 frontend unit tests (all passing)
- [x] **E2E Testing with Playwright** - Comprehensive end-to-end test suite covering all 12 admin management pages:
  - Authentication (login, logout, session persistence, protected routes)
  - Navigation (all admin navigation links)
  - Employees (list, add/edit forms, search, actions, status columns)
  - Users (list, add user, password change dialogs)
  - Auth Roles (role list, add role, permission checkboxes, details)
  - Reports (generation, date range filters, PDF export)
  - Event Logs (log list, details dialog, columns)
  - Org Units (org unit management, view employees)
  - Registered Browsers (browser registration, UUID generation)
  - Timeclock Entries (entries management, date filters, add/edit)
  - Timeclock Frontpage (punch in/out, employee selection)
  - Settings (system settings, theme, logo, license, departments, holiday groups)
- [x] **Generic Table Component Refactoring** - Created reusable `GenericTableComponent` used by all 9 management pages
- [x] **License Reactivation Bug Fix** - Fixed UNIQUE constraint error when reactivating a license that was deactivated offline
- [x] **System Settings Theme Configuration** - Logo upload, theme colors configurable via UI
- [x] **PDF Report Enhancements** - Watermark, improved layout, dept/org headers
- [x] **Database Utilities** - init_database.py, backup_database.py, restore_database.py
- [x] **License Key Generator** - tools/license_generator.py with key pair generation and verification
- [x] **PyInstaller Support** - tep.spec, run_server.py, --executable flag in build_release.py
- [x] **Deployment Documentation** - Comprehensive DEPLOYMENT.md with configuration, database, service management
- [x] **Frontend Web Server Setup** - Single-server deployment: FastAPI serves Angular in production mode
- [x] **Windows Installer** - NSIS installer with config page, shortcuts, firewall rules, uninstaller
- [x] **Backend Service Configuration** - PowerShell script with NSSM for Windows service management
- [x] **Configuration Management** - .env.example template, auto-generated JWT_KEY_PASSWORD in installer
- [x] **Create Deployment Guide** - Comprehensive DEPLOYMENT.md (was listed in Documentation section)
- [x] **Fix Race Condition in Browser Registration** - Removed check-then-act pattern, now uses database constraint with IntegrityError handling
- [x] **Standardize License Enforcement Strategy** - READ operations don't require license, WRITE operations do. Applied consistently across all 11 route modules
- [x] **Add Database Indexes** - Added 5 indexes for performance on licenses, timeclock_entries, and registered_browsers tables
- [x] **Prevent N+1 Query Issues** - Added selectinload() for employee relationships in get_employees() and search_for_employees()
- [x] **Add Badge Number Format Validation** - Added regex pattern to schemas for employee and user badge numbers (alphanumeric, dashes, underscores, 1-20 chars)
- [x] **Scheduled Cleanup for Stale Browser Sessions** - Background task via FastAPI lifespan runs cleanup every 5 minutes

---

## Notes

### Testing Strategy
- Target: 70%+ code coverage
- Focus on critical paths first (authentication, license, timeclock)
- Add integration tests for race conditions

### Running Tests

**Backend Tests (pytest)**:
```bash
cd TEP
python -m pytest tests/ -v
```

**Frontend Unit Tests (Karma/Jasmine)**:
```bash
cd frontend
npm test
```

**E2E Tests (Playwright)**:
```bash
# First, start both servers:
# Terminal 1 - Backend:
cd TEP && python -m uvicorn src.main:app --reload

# Terminal 2 - Frontend:
cd frontend && npm start

# Terminal 3 - Run E2E tests:
cd frontend
npm run e2e              # Run all E2E tests
npm run e2e:headed       # Run with visible browser
npm run e2e:ui           # Interactive UI mode
npm run e2e:debug        # Debug mode
npm run e2e:report       # View HTML report

# Run specific test file:
npx playwright test auth.spec.ts
npx playwright test employees.spec.ts
```

**E2E Test Files** (11 test files in `frontend/e2e/`):
- `auth.spec.ts` - Login, logout, session persistence
- `navigation.spec.ts` - All admin navigation links
- `employees.spec.ts` - Employee management CRUD
- `users.spec.ts` - User management, password change
- `auth-roles.spec.ts` - Role and permission management
- `reports.spec.ts` - Report generation and export
- `event-logs.spec.ts` - Event log viewing
- `org-units.spec.ts` - Org units and registered browsers
- `timeclock.spec.ts` - Timeclock entries and frontpage
- `settings.spec.ts` - System settings, departments, holiday groups
- `example.spec.ts` - Smoke tests, API health, accessibility

### Performance Targets
- API response time: < 200ms for most endpoints
- Frontend load time: < 3s on average connection
- Database query optimization for reports with >1000 entries

### Security Checklist
- [x] Change default root password handling (see High Priority - completed)
- [ ] Review CORS configuration for production
- [ ] Ensure HTTPS in production
- [ ] Regular security audits of dependencies
- [ ] Review authentication token expiration times

---

**Last Updated**: 2026-01-29
