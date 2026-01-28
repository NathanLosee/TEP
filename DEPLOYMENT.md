# TEP Deployment Guide

Complete guide for deploying TEP (Timeclock and Employee Payroll) in production environments.

---

## System Requirements

### Hardware Requirements

**Minimum:**
- Processor: 2 GHz dual-core
- RAM: 4 GB
- Storage: 10 GB available space
- Network: Ethernet or WiFi connection

**Recommended:**
- Processor: 2.5 GHz quad-core or better
- RAM: 8 GB or more
- Storage: 20 GB SSD
- Network: Gigabit Ethernet

### Software Requirements

**Operating System:**
- Windows 10 (64-bit) or newer
- Windows Server 2016 or newer

**Optional (if not using bundled versions):**
- Python 3.13+
- Node.js 18+ (for development/building only)

**Browser Requirements (Client):**
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+ (limited testing)

---

## Pre-Installation Checklist

- [ ] Review system requirements
- [ ] Plan installation directory (e.g., `C:\Program Files\TEP`)
- [ ] Determine network configuration (ports, firewall rules)
- [ ] Plan backup strategy
- [ ] Obtain license key (if required for immediate use)
- [ ] Identify administrator user(s)
- [ ] Review security requirements

---

## Installation Methods

### Method 1: Windows Installer (Recommended)

**For production deployments using pre-built installer.**

1. **Run Installer**
   - Double-click `TEP-Setup-x.x.x.exe`
   - Accept User Account Control prompt

2. **Installation Wizard**
   - Choose installation directory (default: `C:\Program Files\TEP`)
   - Select components:
     - [x] TEP Backend Service (required)
     - [x] TEP Frontend (required)
     - [x] Desktop Shortcut
     - [x] Start Menu Entries
     - [ ] Development Tools (optional)

3. **Configuration**
   - Set backend port (default: 8000)
   - Set root administrator password (minimum 8 characters, 12+ recommended)
   - Configure firewall rules (automatic)

4. **Security Setup**
   - Installer auto-generates secure JWT_KEY_PASSWORD (32-byte random)
   - RSA key pair for JWT authentication is generated on first startup
   - Root administrator password is stored in `.env` file

5. **Service Installation**
   - Installer registers TEP as Windows service
   - Service name: `TEPService`
   - Set to start automatically on boot

6. **Database Initialization**
   - Installer creates empty database
   - Runs Alembic migrations
   - Creates root user

7. **Complete Installation**
   - Launch TEP application
   - Access via desktop shortcut or `http://localhost:8000`
   - In single-server mode, both API and frontend are served on port 8000

### Method 2: Standalone Executable (PyInstaller)

**For deployments without Python installed.**

The build script can create a standalone Windows executable that bundles Python and all dependencies. In production mode, the backend also serves the Angular frontend, providing a **single-server deployment** - no separate web server needed.

1. **Build the Executable**
   ```cmd
   cd TEP
   python scripts/build_release.py --version 1.0.0 --executable
   ```

2. **Locate Output**
   - Build output: `build/TEP-1.0.0/`
   - Backend executable: `build/TEP-1.0.0/backend/tep.exe`
   - Frontend files: `build/TEP-1.0.0/frontend/`
   - Release archive: `releases/TEP-1.0.0.zip`

3. **Deploy to Target Machine**
   - Extract `TEP-1.0.0.zip` to installation directory (e.g., `C:\Program Files\TEP`)
   - No Python installation required
   - All dependencies bundled (~65 MB total)
   - Directory structure should be:
     ```
     C:\Program Files\TEP\
     ├── backend\
     │   ├── tep.exe
     │   ├── _internal\
     │   └── .env           # Create this file
     └── frontend\
         ├── index.html
         ├── main-*.js
         ├── styles-*.css
         └── ...
     ```

4. **Configure Environment**
   Create a `.env` file in the **backend directory** (next to `tep.exe`):
   ```env
   # Required settings
   ENVIRONMENT=production
   ROOT_PASSWORD=YourSecurePassword123!

   # Optional settings
   LOG_LEVEL=INFO
   BACKEND_PORT=8000
   DATABASE_URL=sqlite:///tep_prod.sqlite
   ```

5. **Start Server**
   ```cmd
   cd "C:\Program Files\TEP\backend"
   tep.exe
   ```

   **Expected Output:**
   ```
   Loaded environment from: C:\Program Files\TEP\backend\.env
   ============================================================
   TEP - Timeclock and Employee Payroll
   ============================================================
   Environment: production
   Starting server on 0.0.0.0:8000
   ============================================================
   Initializing database...
   Database initialized successfully.
   INFO:     Serving frontend from: C:\Program Files\TEP\frontend
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```

6. **Access the Application**
   - Open browser to: `http://localhost:8000`
   - The server provides both the API and the Angular frontend
   - API endpoints: `http://localhost:8000/docs` (Swagger UI)
   - Frontend routes are handled by Angular client-side routing

**Note:** In production mode, the database is automatically initialized on first startup using SQLAlchemy's `create_all()`. This creates all required tables if they don't exist.

### Method 3: Manual Installation (Development/Advanced)

**For development or custom deployments.**

See [README.md](README.md) for development setup instructions.

---

## Configuration

### Environment Variables

TEP uses environment variables for configuration. Create a `.env` file in the backend directory or set system environment variables.

**Required Variables:**

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ENVIRONMENT` | Runtime environment | `development` | `production` |
| `ROOT_PASSWORD` | Initial root user password | (none - required in prod) | `MySecurePass123!` |

**Optional Variables:**

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `WARNING`, `ERROR` |
| `DATABASE_URL` | SQLite database path | Auto-generated | `sqlite:///data/tep.sqlite` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:4200` | `https://myapp.com` |
| `BACKEND_PORT` | Server port | `8000` | `8080` |
| `BACKEND_HOST` | Server bind address | `0.0.0.0` | `127.0.0.1` |
| `JWT_KEY_PASSWORD` | Password to encrypt JWT RSA key | (none) | `YourSecretKeyPassword` |

**Example `.env` File:**

```env
# TEP Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO

# Security - CHANGE THESE IN PRODUCTION
ROOT_PASSWORD=ChangeThisSecurePassword123!

# Database
DATABASE_URL=sqlite:///tep_prod.sqlite

# CORS - Set to your frontend domain (in single-server mode, this may not be needed)
CORS_ORIGINS=https://timeclock.yourcompany.com

# Server
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Security - Password for encrypting JWT RSA private key
JWT_KEY_PASSWORD=YourSecureKeyEncryptionPassword
```

### Database Paths

The database location is determined by:

1. `DATABASE_URL` environment variable (if set)
2. Automatic based on `ENVIRONMENT`:
   - Production: `sqlite:///tep_prod.sqlite`
   - Development: `sqlite:///tep_dev.sqlite`

**Important:** The database file is created relative to the working directory. When running as a service, ensure the working directory is set correctly.

### Database Initialization

**Method 1: Using Alembic (Recommended)**

```cmd
# Navigate to project directory
cd "C:\Program Files\TEP\backend"

# Run all migrations
alembic upgrade head
```

**Method 2: Using Init Script**

```cmd
cd "C:\Program Files\TEP"
python scripts/init_database.py

# With custom path
python scripts/init_database.py --db-path "C:\Data\tep.sqlite"

# Force reinitialize (WARNING: deletes existing data)
python scripts/init_database.py --force
```

**Method 3: Copy Pre-initialized Database**

For standalone executable deployments, you can copy a pre-initialized database:

```cmd
# From development environment
copy "tep_dev.sqlite" "C:\Program Files\TEP\backend\tep_prod.sqlite"
```

### First Startup Behavior

On first startup, TEP automatically:

1. **Checks Database** - Verifies database exists and has correct schema
2. **Creates Root User** - If no root user exists:
   - Uses `ROOT_PASSWORD` environment variable
   - In production: **Fails if `ROOT_PASSWORD` not set**
   - In development: Generates random password (displayed in console)
3. **Validates License** - Checks for active license (admin features locked if none)

---

## Initial Configuration

### First Launch

1. **Access Application**
   - Open browser to `http://localhost:8000` (or configured port)
   - Or use desktop shortcut
   - In single-server mode, the API and frontend are both on the same port

2. **Login as Root User**
   - Username: `0` (badge number zero)
   - Password: (set during installation)

3. **Activate License** (if required)
   - Navigate to: Admin → License Management
   - Enter license key
   - Click "Activate License"
   - Verify activation status

4. **Create Organizational Structure**
   - Navigate to: Admin → Org Units
   - Create primary organizational unit
   - Add departments as needed

5. **Add First Employees**
   - Navigate to: Admin → Employees
   - Create employee records
   - Assign to organizational units

6. **Configure Auth Roles**
   - Navigate to: Admin → Auth Roles
   - Review default permissions
   - Create custom roles as needed

7. **Register Browsers** (for timeclock)
   - Navigate to: Admin → Registered Browsers
   - Register company devices for timeclock
   - Note UUIDs for device recovery

### Security Hardening

1. **Change Default Root Password**
   ```
   - Login as root user
   - Navigate to profile menu
   - Select "Change Password"
   - Use strong password (16+ characters)
   ```

2. **Review CORS Settings**
   - Edit configuration file: `C:\Program Files\TEP\config\.env`
   - Set `CORS_ORIGINS` to your domain
   - Example: `CORS_ORIGINS=https://yourdomain.com`

3. **Configure Firewall**
   - Ensure only necessary ports are open
   - Backend: Port 8000 (or configured port)
   - Frontend: Port 4200 (or configured port)
   - Restrict access to internal network if possible

4. **Enable HTTPS** (recommended)
   - Obtain SSL certificate
   - Configure reverse proxy (Nginx/IIS)
   - Update frontend API URL to use HTTPS

5. **Review Event Logging**
   - Check event log configuration
   - Ensure audit trail is enabled
   - Plan for log rotation/archival

---

## Network Configuration

### Port Configuration

**Single-Server Mode (Standalone Executable):**
- Only one port needed: `8000` (default)
- Backend serves both API and frontend

**Separate Frontend Mode (Development):**
- Backend API: `8000`
- Frontend dev server: `4200`

**To Change Port:**

1. Stop TEP service
2. Edit `.env` file:
   ```env
   BACKEND_PORT=8080
   ```
3. Restart TEP service

### Firewall Rules

**Windows Firewall:**

Allow inbound connections:
```powershell
# Backend API
netsh advfirewall firewall add rule name="TEP Backend" dir=in action=allow protocol=TCP localport=8000

# Frontend (if serving separately)
netsh advfirewall firewall add rule name="TEP Frontend" dir=in action=allow protocol=TCP localport=4200
```

**Internal Network Only:**
- Restrict source to local network subnet
- Example: 192.168.1.0/24

---

## Database Management

### Database Location

The database location depends on configuration:

| Environment | Default Location |
|-------------|------------------|
| Production | `tep_prod.sqlite` (in working directory) |
| Development | `tep_dev.sqlite` (in working directory) |
| Custom | Set via `DATABASE_URL` environment variable |

**Recommended Production Location:**
```
C:\Program Files\TEP\data\tep_prod.sqlite
```

To use a custom location, set the environment variable:
```cmd
set DATABASE_URL=sqlite:///C:/ProgramData/TEP/tep.sqlite
```

### Backup Database

**Recommended Schedule:** Daily backups with 30-day retention

**Using Backup Script:**

```cmd
# Basic backup (creates timestamped file in ./backups/)
python scripts/backup_database.py

# Backup with compression
python scripts/backup_database.py --compress

# Custom paths
python scripts/backup_database.py --db-path "C:\Data\tep.sqlite" --output-dir "D:\Backups"

# Cleanup old backups (keep 30 most recent)
python scripts/backup_database.py --cleanup --keep 30
```

**Backup Output:**
- Uncompressed: `backups/tep_YYYYMMDD_HHMMSS.sqlite`
- Compressed: `backups/tep_YYYYMMDD_HHMMSS.sqlite.gz`

**Manual Backup:**

```cmd
# Stop service first (recommended but not required for SQLite)
net stop TEPService

# Copy database
copy "C:\Program Files\TEP\data\tep_prod.sqlite" "C:\Backups\tep_backup.sqlite"

# Restart service
net start TEPService
```

**Automated Backup (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "TEP Daily Backup"
4. Trigger: Daily at 2:00 AM
5. Action: Start a program
   - Program: `python`
   - Arguments: `scripts/backup_database.py --compress --cleanup`
   - Start in: `C:\Program Files\TEP`

### Restore Database

**Using Restore Script (Recommended):**

```cmd
# Restore from backup (creates safety backup first)
python scripts/restore_database.py backups/tep_20260113_120000.sqlite

# Restore compressed backup (auto-detected)
python scripts/restore_database.py backups/tep_20260113_120000.sqlite.gz

# Restore with verification
python scripts/restore_database.py backups/tep_backup.sqlite --verify

# Skip confirmation prompt
python scripts/restore_database.py backups/tep_backup.sqlite --force
```

**Manual Restore:**

```cmd
# Stop service
net stop TEPService

# Backup current database (safety)
copy "C:\Program Files\TEP\data\tep_prod.sqlite" "C:\Program Files\TEP\data\tep_before_restore.sqlite"

# Restore backup
copy "C:\Backups\tep_backup.sqlite" "C:\Program Files\TEP\data\tep_prod.sqlite"

# Restart service
net start TEPService
```

### Database Initialization

**Initialize New Database:**

```cmd
# Initialize with default settings
python scripts/init_database.py

# Custom database path
python scripts/init_database.py --db-path "C:\Data\tep.sqlite"

# Initialize and verify schema
python scripts/init_database.py --verify

# Force reinitialize (WARNING: deletes all data!)
python scripts/init_database.py --force
```

**Expected Tables:**
- `alembic_version` - Migration tracking
- `auth_roles`, `auth_role_permissions`, `auth_role_memberships` - Authorization
- `departments`, `department_memberships` - Organization
- `employees` - Employee records
- `event_logs` - Audit trail
- `holiday_groups`, `holidays` - Holiday scheduling
- `licenses` - License management
- `org_units` - Organizational units
- `registered_browsers` - Device registration
- `timeclock_entries` - Time tracking
- `users` - User accounts
- `system_settings` - Application settings

### Database Maintenance

**Check Integrity:**
```cmd
sqlite3 "tep_prod.sqlite" "PRAGMA integrity_check;"
```

**Optimize Database (Monthly):**
```cmd
sqlite3 "tep_prod.sqlite" "VACUUM;"
```

**Analyze for Query Optimization:**
```cmd
sqlite3 "tep_prod.sqlite" "ANALYZE;"
```

---

## License Management

### Activating License

1. **Obtain License Key**
   - Contact vendor for license key
   - License format: 128-character hexadecimal string

2. **Activate in Application**
   - Login as administrator
   - Navigate to: Admin → License Management
   - Enter license key in input field
   - Click "Activate License"

3. **Verify Activation**
   - License status should show "Active"
   - Activated date displayed
   - Admin features now unlocked

### License Status

**Check License Status:**
- Navigate to: Admin Dashboard
- License status widget shows current status

**Programmatic Check:**
```bash
curl http://localhost:8000/licenses/status
```

Response:
```json
{
  "is_active": true,
  "license_key": "abc123...",
  "activated_at": "2026-01-13T12:00:00",
  "server_id": null
}
```

### Deactivating License

**To deactivate (e.g., for server migration):**

1. Navigate to: Admin → License Management
2. Click "Deactivate License"
3. Confirm deactivation
4. Admin features will be locked

---

## Service Management

### Running the Standalone Executable

**For PyInstaller builds without Windows service:**

```cmd
# Navigate to backend directory
cd "C:\Program Files\TEP\backend"

# Set required environment variables
set ENVIRONMENT=production
set ROOT_PASSWORD=YourSecurePassword123!
set DATABASE_URL=sqlite:///tep_prod.sqlite

# Run the server
tep.exe
```

**Expected Output:**
```
============================================================
TEP - Timeclock and Employee Payroll
============================================================
Environment: production
Starting server on 0.0.0.0:8000
============================================================
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Running in Background (PowerShell):**
```powershell
Start-Process -FilePath "C:\Program Files\TEP\backend\tep.exe" -WindowStyle Hidden
```

### TEP Windows Service

**Service Name:** `TEPService`

**Start Service:**
```cmd
net start TEPService
```

**Stop Service:**
```cmd
net stop TEPService
```

**Restart Service:**
```cmd
net stop TEPService && net start TEPService
```

**Check Service Status:**
```cmd
sc query TEPService
```

**Installing as Windows Service (using NSSM):**

If you want to run the standalone executable as a Windows service, use the included install script:

```powershell
# Run as Administrator
cd "C:\Program Files\TEP"

# Install service (downloads NSSM automatically if needed)
.\scripts\install-service.ps1 -InstallDir "C:\Program Files\TEP" -Port 8000

# Or with custom service name
.\scripts\install-service.ps1 -InstallDir "C:\Program Files\TEP" -ServiceName "TEPService" -Port 8000

# Uninstall service
.\scripts\install-service.ps1 -Uninstall
```

The script will:
- Download NSSM automatically if not present
- Configure the service with auto-start on boot
- Set up log rotation for stdout/stderr
- Configure automatic restart on failure
- Prompt to start the service immediately

**Alternative: Manual NSSM Installation**

```cmd
# Download NSSM from https://nssm.cc/
# Install service
nssm install TEPService "C:\Program Files\TEP\backend\tep.exe"

# Set working directory
nssm set TEPService AppDirectory "C:\Program Files\TEP\backend"

# Configure startup
nssm set TEPService Start SERVICE_AUTO_START

# Start service
nssm start TEPService
```

Note: Environment variables are read from the `.env` file in the backend directory, so you don't need to set them via NSSM.

### Service Configuration

**Automatic Startup:**
```cmd
sc config TEPService start=auto
```

**Manual Startup:**
```cmd
sc config TEPService start=demand
```

**Service Recovery:**
```cmd
# Restart on failure
sc failure TEPService reset=86400 actions=restart/60000/restart/60000/restart/60000
```

### Logs

**Service Logs Location:**
```
C:\Program Files\TEP\logs\service.log
C:\Program Files\TEP\logs\application.log
```

**View Recent Logs:**
```cmd
type "C:\Program Files\TEP\logs\application.log" | more
```

---

## Updates and Upgrades

### Checking for Updates

**Method 1: Application (future feature)**
- Navigate to: Admin → System → Updates

**Method 2: Manual Check**
- Check with vendor for latest version
- Review release notes

### Applying Updates

1. **Backup Current Installation**
   ```cmd
   # Backup database
   scripts\backup_database.exe

   # Backup configuration
   copy "C:\Program Files\TEP\config\.env" "C:\Backups\tep_config_backup.env"
   ```

2. **Stop Service**
   ```cmd
   net stop TEPService
   ```

3. **Run Update Installer**
   - Execute: `TEP-Update-x.x.x.exe`
   - Follow upgrade wizard
   - Installer preserves database and configuration

4. **Verify Update**
   - Service starts automatically
   - Login and verify functionality
   - Check version: Admin → System → About

5. **Run Database Migrations** (if needed)
   ```cmd
   cd "C:\Program Files\TEP"
   scripts\migrate_database.exe
   ```

### Rolling Back

**If update fails:**

1. Stop service
2. Restore database backup
3. Reinstall previous version
4. Restore configuration
5. Start service

---

## Troubleshooting

### Service Won't Start

**Check Windows Event Viewer:**
```
Event Viewer → Windows Logs → Application
Look for errors from "TEPService"
```

**Common Causes:**
- Port already in use
- Database file locked/corrupted
- Missing configuration file
- Insufficient permissions

**Solutions:**
```cmd
# Check port availability
netstat -ano | findstr :8000

# Verify database integrity
sqlite3 "C:\Program Files\TEP\data\tep.sqlite" "PRAGMA integrity_check;"

# Check file permissions
icacls "C:\Program Files\TEP"
```

### Cannot Connect to Application

**Verify Service is Running:**
```cmd
sc query TEPService
```

**Check Firewall:**
```cmd
netsh advfirewall firewall show rule name="TEP Backend"
```

**Test Backend API:**
```cmd
curl http://localhost:8000
```

Expected response: `{"message": "Welcome to Timeclock and Employee Payroll!"}`

**Check Frontend:**
- Navigate to: `http://localhost:4200`
- Check browser console for errors (F12)

### Database Errors

**Error: "Database is locked"**
- Another process is accessing database
- Stop service and retry
- Check for zombie processes

**Error: "Database disk image is malformed"**
- Database corruption
- Restore from backup immediately

### Login Issues

**Cannot Login as Root:**
- Verify root user exists in database
- Reset root password using recovery tool:
  ```cmd
  scripts\reset_root_password.exe
  ```

**Session Expired:**
- JWT tokens expire after inactivity
- Simply login again
- Check system time is synchronized

### License Issues

**License Won't Activate:**
- Verify license key format (128 hex characters)
- Check internet connection (if phone-home required)
- Contact vendor for support

**Admin Features Locked:**
- Check license status
- License may have expired or been deactivated
- Re-activate license

---

## Performance Optimization

### Database Optimization

**For databases >10,000 entries:**

1. **Add Indexes** (if not present):
   ```sql
   CREATE INDEX IF NOT EXISTS idx_badge_number ON employees(badge_number);
   CREATE INDEX IF NOT EXISTS idx_timeclock_registered ON timeclock_entries(registered_at);
   CREATE INDEX IF NOT EXISTS idx_license_active ON licenses(is_active);
   ```

2. **Regular Vacuuming:**
   ```cmd
   sqlite3 "C:\Program Files\TEP\data\tep.sqlite" "VACUUM;"
   ```

### Application Performance

**Increase Worker Processes** (if using separate WSGI server):
- Edit configuration
- Increase `WORKERS` setting
- Recommended: 2 × CPU cores

**Enable Response Caching:**
- Configure in environment variables
- Set reasonable TTL values

---

## Security Best Practices

### Regular Security Tasks

- [ ] Change root password every 90 days
- [ ] Review auth roles and permissions quarterly
- [ ] Audit event logs monthly
- [ ] Update software when patches available
- [ ] Review registered browsers quarterly (remove unused)
- [ ] Backup encryption keys securely
- [ ] Test disaster recovery annually

### Securing the Database

1. **File System Permissions:**
   ```cmd
   # Only allow SYSTEM and Administrators
   icacls "C:\Program Files\TEP\data" /inheritance:r
   icacls "C:\Program Files\TEP\data" /grant:r SYSTEM:(OI)(CI)F
   icacls "C:\Program Files\TEP\data" /grant:r Administrators:(OI)(CI)F
   ```

2. **Encrypt Backups:**
   - Use Windows EFS or BitLocker
   - Store backups on separate secured location

### Network Security

- [ ] Use HTTPS in production (obtain SSL certificate)
- [ ] Restrict CORS to specific domains
- [ ] Use firewall to limit access to internal network
- [ ] Consider VPN for remote access
- [ ] Implement fail2ban or similar for brute-force protection

---

## Uninstallation

### Using Uninstaller

1. **Backup Data First**
   ```cmd
   scripts\backup_database.exe
   copy "C:\Program Files\TEP\config\.env" "C:\Backups\tep_config.env"
   ```

2. **Run Uninstaller**
   - Control Panel → Programs → Uninstall a Program
   - Select "TEP - Timeclock and Employee Payroll"
   - Click Uninstall
   - Follow prompts

3. **Choose Data Retention**
   - Option: Keep database and configuration
   - Option: Remove all data

### Manual Uninstallation

1. Stop and remove service:
   ```cmd
   net stop TEPService
   sc delete TEPService
   ```

2. Remove program files:
   ```cmd
   rmdir /s "C:\Program Files\TEP"
   ```

3. Remove start menu shortcuts:
   ```cmd
   del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\TEP"
   ```

4. Remove desktop shortcut (if exists)

---

## Support and Resources

### Documentation
- User Manual: `docs/USER_MANUAL.md`
- API Documentation: `http://localhost:8000/docs`
- Development Guide: `README.md`

### System Information

**Version Information:**
- Navigate to: Admin → System → About
- Shows: Application version, database version, license status

**Log Files:**
- Application logs: `C:\Program Files\TEP\logs\application.log`
- Service logs: `C:\Program Files\TEP\logs\service.log`
- Error logs: `C:\Program Files\TEP\logs\error.log`

### Contact Support

When contacting support, provide:
- TEP version number
- Operating system version
- Error messages (from logs)
- Steps to reproduce issue
- License key (if applicable)

---

## Build Scripts Reference

### build_release.py

Creates a production release package.

```cmd
# Source distribution (requires Python on target)
python scripts/build_release.py --version 1.0.0

# Standalone executable (PyInstaller)
python scripts/build_release.py --version 1.0.0 --executable

# With Windows installer (NSIS)
python scripts/build_release.py --version 1.0.0 --executable --installer

# Skip tests for quick builds
python scripts/build_release.py --version 1.0.0 --executable --skip-tests

# Custom output directory
python scripts/build_release.py --version 1.0.0 --output-dir ./my-build
```

**Output Structure:**
```
build/TEP-1.0.0/
├── backend/           # Backend executable or source
│   ├── tep.exe        # (executable mode)
│   ├── _internal/     # (executable mode) bundled dependencies
│   └── ...
├── frontend/          # Angular production build
├── database/          # Migration scripts
├── config/            # Configuration templates
│   └── .env.example
├── scripts/           # Utility scripts
│   ├── backup_database.py
│   └── license_generator.py
└── docs/              # Documentation
    ├── README.md
    └── VERSION.json
```

### Database Scripts

| Script | Description |
|--------|-------------|
| `scripts/init_database.py` | Initialize new database with schema |
| `scripts/backup_database.py` | Create timestamped backups |
| `scripts/restore_database.py` | Restore from backup file |

### License Tools

| Script | Description |
|--------|-------------|
| `tools/license_generator.py` | Generate Ed25519 key pairs and license keys |

### Service Management Scripts

| Script | Description |
|--------|-------------|
| `scripts/install-service.ps1` | Install/uninstall TEP as Windows service using NSSM |

---

**Document Version:** 1.2
**Last Updated:** 2026-01-27
**Compatible with:** TEP v1.0.0+
