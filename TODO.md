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

- [ ] **Document and Standardize License Enforcement Strategy**
  - **Question**: Should READ operations require a license?
  - **Issue**: License checks inconsistently applied (some GET endpoints have it, others don't)
  - **Solution**:
    1. Document the strategy (which operations need license)
    2. Apply consistently across all admin routes
  - **Files**: All route files in admin modules
  - **Priority**: MEDIUM - Feature clarity

- [ ] **Fix Race Condition in Browser Registration**
  - **Issue**: Check-then-act pattern without transaction lock
  - **File**: `src/registered_browser/routes.py:68-75`
  - **Solution**: Rely on database unique constraint + catch `IntegrityError`
  - **Example**:
    ```python
    try:
        browser = browser_repository.create_registered_browser(request, db)
    except IntegrityError:
        raise HTTPException(409, "UUID already exists")
    ```
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

- [ ] **Add Database Indexes**
  - **Recommendation**: Add indexes on frequently queried fields:
    - `employees.badge_number` (employee lookups are frequent)
    - `licenses.is_active` (license status checks)
    - `timeclock_entries.registered_at` (timeclock queries)
    - `timeclock_entries.last_seen` (session tracking)
  - **Priority**: LOW - Performance

- [ ] **Prevent N+1 Query Issues**
  - **Areas to Check**:
    - Employee queries with manager relationships
    - Timeclock entries with employee details
  - **Solution**: Add `selectinload()` for eager loading where needed
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

- [ ] **Scheduled Cleanup for Stale Browser Sessions**
  - **Current**: Manual cleanup called in verify endpoint
  - **File**: `src/registered_browser/routes.py:119-120`
  - **Solution**: Use scheduled task or middleware for automatic cleanup
  - **Priority**: LOW - Architecture improvement

### Validation

- [ ] **Add Badge Number Format Validation**
  - **Issue**: No regex validation on badge numbers
  - **Impact**: Users could create invalid badge numbers (e.g., "!!!" or spaces)
  - **Files**: `src/employee/routes.py`, `src/user/routes.py`
  - **Solution**: Add regex pattern to schemas
  - **Priority**: LOW - Data quality

- [ ] **Add Server ID Format Validation**
  - **File**: `src/license/schemas.py:19`
  - **Issue**: No format validation for `server_id` if provided
  - **Solution**: Add regex or format validator
  - **Priority**: LOW - Data quality

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
- [x] **Add Comprehensive Testing** - 233 backend + 325 frontend tests (all passing)
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

---

## Notes

### Testing Strategy
- Target: 70%+ code coverage
- Focus on critical paths first (authentication, license, timeclock)
- Add integration tests for race conditions

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

**Last Updated**: 2026-01-27
