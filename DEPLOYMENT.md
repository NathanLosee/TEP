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
   - Set frontend port (default: 4200)
   - Configure firewall rules (automatic)

4. **Security Setup**
   - Installer generates RSA key pair for JWT authentication
   - Set root administrator password (required)
   - Password requirements: minimum 12 characters

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
   - Access via desktop shortcut or `http://localhost:4200`

### Method 2: Manual Installation (Development/Advanced)

**For development or custom deployments.**

See [README.md](README.md) for development setup instructions.

---

## Initial Configuration

### First Launch

1. **Access Application**
   - Open browser to `http://localhost:4200` (or configured port)
   - Or use desktop shortcut

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

**Default Ports:**
- Backend API: `8000`
- Frontend: `4200`

**To Change Ports:**

1. Stop TEP service
2. Edit configuration:
   ```
   File: C:\Program Files\TEP\config\.env

   # Backend port
   BACKEND_PORT=8000

   # Frontend (requires rebuild)
   FRONTEND_PORT=4200
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

**Default Location:**
```
C:\Program Files\TEP\data\tep.sqlite
```

### Backup Database

**Recommended Schedule:** Daily backups with weekly archival

**Manual Backup:**

1. **Using Bundled Script:**
   ```cmd
   cd "C:\Program Files\TEP"
   scripts\backup_database.exe
   ```
   Backup saved to: `C:\Program Files\TEP\backups\tep_YYYYMMDD_HHMMSS.sqlite`

2. **Manual Copy:**
   ```cmd
   # Stop service first
   net stop TEPService

   # Copy database
   copy "C:\Program Files\TEP\data\tep.sqlite" "C:\Backups\tep_backup.sqlite"

   # Restart service
   net start TEPService
   ```

**Automated Backup (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "TEP Daily Backup"
4. Trigger: Daily at 2:00 AM
5. Action: Start a program
   - Program: `C:\Program Files\TEP\scripts\backup_database.exe`
6. Finish

### Restore Database

**To restore from backup:**

```cmd
# Stop service
net stop TEPService

# Backup current database (safety)
copy "C:\Program Files\TEP\data\tep.sqlite" "C:\Program Files\TEP\data\tep_before_restore.sqlite"

# Restore backup
copy "C:\Backups\tep_backup.sqlite" "C:\Program Files\TEP\data\tep.sqlite"

# Restart service
net start TEPService
```

**Using Restore Script:**
```cmd
cd "C:\Program Files\TEP"
scripts\restore_database.exe "C:\Backups\tep_backup.sqlite"
```

### Database Maintenance

**Optimize Database (Monthly):**
```cmd
cd "C:\Program Files\TEP"
scripts\optimize_database.exe
```

**Check Database Integrity:**
```cmd
sqlite3 "C:\Program Files\TEP\data\tep.sqlite" "PRAGMA integrity_check;"
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

**Document Version:** 1.0
**Last Updated:** 2026-01-13
**Compatible with:** TEP v1.0.0+
