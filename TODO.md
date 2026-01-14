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

- [ ] **Standardize Import Organization**
  - **Issue**: Mix of relative and absolute imports across codebase
  - **Solution**: Use aliased absolute imports throughout (e.g., `import src.module.routes as module_routes`)
  - **Files**: All route and service files
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

- [ ] **Make Material Design Theme Configurable via Environment Variables**
  - **Scope**:
    - Surface colors (primary, secondary, tertiary)
    - Background colors
    - Logo URL/path used on frontend
    - Brand colors
  - **Files**:
    - `frontend/src/environments/environment.ts`
    - `frontend/src/environments/environment.development.ts`
    - `frontend/src/styles.scss`
  - **Implementation**:
    1. Add theme variables to environment files
    2. Create theme configuration service
    3. Dynamically apply CSS variables based on config
    4. Allow logo replacement via environment variable
  - **Priority**: LOW - Customization
  - **Benefit**: Easy theme customization without code changes

- [ ] **Enhance PDF Report Appearance**
  - **Current State**: Reports are plain and functional
  - **File**: `src/report/service.py` (PDF generation logic)
  - **Proposed Enhancements**:
    1. **Logo Integration**:
       - Add company logo as large background watermark (semi-transparent)
       - OR add logo in header/corner of each page
       - Make logo path configurable via environment variable
    2. **Layout Improvements**:
       - Start employee timeclock details on same page as summaries (reduce whitespace)
       - Improve table alignment and spacing
       - Add professional header/footer with page numbers
    3. **Styling Enhancements**:
       - Add color to headers (use theme colors from config)
       - Better typography hierarchy
       - Improved border styles for tables
       - Add subtle background colors for alternating rows
    4. **Additional Elements**:
       - Report generation date/time in header
       - Company name/info in header (from config)
       - Report title with styling
       - Summary box with key metrics highlighted
  - **Technical Approach**:
    - Use ReportLab's `canvas.drawImage()` for watermark
    - Create reusable template with header/footer
    - Define style constants at top of file for easy customization
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

- [ ] **Create Deployment Guide**
  - **Topics**:
    - Production environment setup
    - Environment variable configuration
    - Database backup strategies
    - SSL/HTTPS setup
    - CORS configuration for production
  - **Priority**: LOW - Documentation

---

## Packaging & Deployment

### Production Packaging

- [ ] **Create Production Build Scripts**
  - **Backend**:
    - Script to bundle Python application with dependencies
    - Generate standalone executable (PyInstaller or similar)
    - Include all required assets (migrations, keys directory structure)
  - **Frontend**:
    - Production build configuration
    - AOT compilation
    - Asset optimization and minification
  - **Files to Create**:
    - `scripts/build_backend.py` - Backend packaging script
    - `scripts/build_frontend.sh` - Frontend build script
    - `scripts/package_release.py` - Complete release packager
  - **Priority**: HIGH - Required for distribution

- [ ] **Create Installation Package**
  - **Type**: Windows installer (.msi or .exe)
  - **Contents**:
    - Backend executable
    - Frontend static files
    - Database initialization scripts
    - Default configuration templates
    - License activation tool
  - **Installer Features**:
    - Custom installation directory selection
    - Service installation option
    - Desktop shortcut creation
    - Start menu entries
    - Automatic database initialization
  - **Tools**:
    - NSIS (Nullsoft Scriptable Install System)
    - Or WiX Toolset for MSI
  - **Priority**: HIGH - Required for distribution

- [ ] **Create Deployment Documentation**
  - **Topics**:
    - System requirements
    - Installation steps
    - Initial configuration
    - License activation process
    - Backup procedures
    - Update/upgrade process
    - Uninstallation
    - Troubleshooting common issues
  - **File**: `DEPLOYMENT.md`
  - **Priority**: HIGH - Required for distribution

- [ ] **Backend Service Configuration**
  - **Windows Service**:
    - Create Windows service wrapper for backend
    - Auto-start on boot
    - Graceful shutdown handling
    - Service logging
  - **Tools**: NSSM (Non-Sucking Service Manager) or custom service wrapper
  - **Priority**: HIGH - Production requirement

- [ ] **Frontend Web Server Setup**
  - **Options**:
    1. Bundle with lightweight web server (e.g., Nginx for Windows)
    2. Or serve frontend directly from FastAPI
  - **Configuration**:
    - Static file serving
    - Gzip compression
    - Cache headers
    - Reverse proxy setup (if using separate web server)
  - **Priority**: HIGH - Production requirement

- [ ] **Database Bundling**
  - **Approach**:
    - Bundle empty SQLite database with schema
    - Run migrations on first startup
    - Provide backup/restore utilities
  - **Files to Create**:
    - `scripts/init_database.py` - Initialize database
    - `scripts/backup_database.py` - Backup utility
    - `scripts/restore_database.py` - Restore utility
  - **Priority**: HIGH - Production requirement

- [ ] **Configuration Management**
  - **Default Configuration**:
    - Bundle template `.env.example` file
    - Installer prompts for critical settings (port, passwords)
    - Create configuration UI (optional, future enhancement)
  - **Security**:
    - Generate unique RSA keys during installation
    - Prompt for secure root password
    - Generate random JWT secret
  - **Priority**: HIGH - Production requirement

- [ ] **License Key Generator Tool**
  - **Purpose**: Separate tool for generating license keys
  - **Features**:
    - Generate Ed25519 key pair (one-time setup)
    - Generate signed license keys
    - Revocation support (future)
  - **Security**: Keep private key separate from application
  - **File**: `tools/license_generator.py`
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
- [ ] Change default root password handling
- [ ] Review CORS configuration for production
- [ ] Ensure HTTPS in production
- [ ] Regular security audits of dependencies
- [ ] Review authentication token expiration times

---

**Last Updated**: 2026-01-13
