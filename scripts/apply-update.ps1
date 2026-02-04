<#
.SYNOPSIS
    Apply a TAP update or rollback to a previous version.

.DESCRIPTION
    This script is launched by the TAP backend after an update is downloaded.
    It waits for tap.exe to exit, backs up the current backend, extracts the
    update zip, copies new files (preserving .env, data, and logs), then
    restarts the application.

.PARAMETER BackendDir
    Path to the backend directory containing tap.exe.

.PARAMETER UpdateZip
    Path to the downloaded update zip file.

.PARAMETER ServiceName
    Name of the Windows service. Default: TAPService

.PARAMETER Rollback
    Perform a rollback instead of an update.

.PARAMETER BackupDir
    Path to the backup directory to restore from (used with -Rollback).

.EXAMPLE
    .\apply-update.ps1 -BackendDir "C:\Program Files\TAP\backend" -UpdateZip "C:\Program Files\TAP\backend\updates\TAP-1.1.0.zip"

.EXAMPLE
    .\apply-update.ps1 -BackendDir "C:\Program Files\TAP\backend" -Rollback -BackupDir "C:\Program Files\TAP\backend-backup-20260201-120000"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$BackendDir,

    [string]$UpdateZip,

    [string]$ServiceName = "TAPService",

    [switch]$Rollback,

    [string]$BackupDir
)

$ErrorActionPreference = "Stop"

# Set up logging
$installDir = Split-Path $BackendDir -Parent
$logDir = Join-Path $installDir "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
$logFile = Join-Path $logDir "update.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logFile -Value $entry
    Write-Host $entry
}

function Wait-ForProcessExit {
    param([string]$ProcessName = "tap", [int]$TimeoutSeconds = 60)

    Write-Log "Waiting for $ProcessName.exe to exit (timeout: ${TimeoutSeconds}s)..."
    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        $proc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
        if (-not $proc) {
            Write-Log "$ProcessName.exe has exited"
            return $true
        }
        Start-Sleep -Seconds 2
        $elapsed += 2
    }

    Write-Log "Timeout waiting for $ProcessName.exe to exit" "WARN"
    # Try to kill it
    $proc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Log "Force-killing $ProcessName.exe" "WARN"
        Stop-Process -Name $ProcessName -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    return $true
}

function Stop-TapService {
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq "Running") {
        Write-Log "Stopping service $ServiceName..."
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
}

function Start-TapService {
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Log "Starting service $ServiceName..."
        Start-Service -Name $ServiceName -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service.Status -eq "Running") {
            Write-Log "Service started successfully"
        } else {
            Write-Log "Service may not have started. Status: $($service.Status)" "WARN"
        }
    } else {
        # No service - start tap.exe directly
        $tapExe = Join-Path $BackendDir "tap.exe"
        if (Test-Path $tapExe) {
            Write-Log "Starting tap.exe directly..."
            Start-Process -FilePath $tapExe -WorkingDirectory $BackendDir -WindowStyle Hidden
        } else {
            Write-Log "tap.exe not found at $tapExe" "ERROR"
        }
    }
}

# Directories/files to preserve during updates
$preserveItems = @(".env", "data", "logs", "updates")

function Apply-Update {
    Write-Log "=== Starting update apply ==="
    Write-Log "Backend directory: $BackendDir"
    Write-Log "Update zip: $UpdateZip"

    # Validate inputs
    if (-not (Test-Path $BackendDir)) {
        Write-Log "Backend directory not found: $BackendDir" "ERROR"
        exit 1
    }
    if (-not (Test-Path $UpdateZip)) {
        Write-Log "Update zip not found: $UpdateZip" "ERROR"
        exit 1
    }

    # Stop service and wait for process to exit
    Stop-TapService
    Wait-ForProcessExit

    # Create timestamped backup
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupPath = Join-Path $installDir "backend-backup-$timestamp"
    Write-Log "Creating backup at: $backupPath"

    # Copy backend dir to backup, excluding preserved items
    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    Get-ChildItem -Path $BackendDir | Where-Object {
        $preserveItems -notcontains $_.Name
    } | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $backupPath -Recurse -Force
    }
    Write-Log "Backup created successfully"

    # Extract update to temp directory
    $extractPath = Join-Path $env:TEMP "tap-update-extract"
    if (Test-Path $extractPath) {
        Remove-Item $extractPath -Recurse -Force
    }
    Write-Log "Extracting update zip..."
    Expand-Archive -Path $UpdateZip -DestinationPath $extractPath -Force

    # Find the backend directory in the extracted zip
    # Expected structure: TAP-x.x.x/backend/
    $extractedBackend = $null
    $topDirs = Get-ChildItem -Path $extractPath -Directory
    foreach ($dir in $topDirs) {
        $candidate = Join-Path $dir.FullName "backend"
        if (Test-Path $candidate) {
            $extractedBackend = $candidate
            break
        }
    }

    if (-not $extractedBackend) {
        # Maybe the zip directly contains backend files
        if (Test-Path (Join-Path $extractPath "tap.exe")) {
            $extractedBackend = $extractPath
        } else {
            Write-Log "Could not find backend directory in update zip" "ERROR"
            Write-Log "Restoring from backup..."
            Restore-Backup -BackupPath $backupPath
            exit 1
        }
    }

    # Copy new files over existing, skipping preserved items
    Write-Log "Copying updated files..."
    Get-ChildItem -Path $extractedBackend | Where-Object {
        $preserveItems -notcontains $_.Name
    } | ForEach-Object {
        $destPath = Join-Path $BackendDir $_.Name
        if (Test-Path $destPath) {
            Remove-Item $destPath -Recurse -Force
        }
        Copy-Item -Path $_.FullName -Destination $destPath -Recurse -Force
    }

    # Clean up temp extraction
    Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue

    # Clean up old backups (keep only the 3 most recent)
    $allBackups = Get-ChildItem -Path $installDir -Directory -Filter "backend-backup-*" |
        Sort-Object Name -Descending
    if ($allBackups.Count -gt 3) {
        $allBackups | Select-Object -Skip 3 | ForEach-Object {
            Write-Log "Removing old backup: $($_.Name)"
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    Write-Log "Update applied successfully"

    # Restart
    Start-TapService
    Write-Log "=== Update complete ==="
}

function Restore-Backup {
    param([string]$BackupPath)

    if (-not $BackupPath) {
        $BackupPath = $BackupDir
    }

    Write-Log "=== Starting rollback ==="
    Write-Log "Restoring from: $BackupPath"

    if (-not (Test-Path $BackupPath)) {
        Write-Log "Backup directory not found: $BackupPath" "ERROR"
        exit 1
    }

    # Stop service and wait for process
    Stop-TapService
    Wait-ForProcessExit

    # Remove current files (except preserved items)
    Get-ChildItem -Path $BackendDir | Where-Object {
        $preserveItems -notcontains $_.Name
    } | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force
    }

    # Copy backup files back
    Get-ChildItem -Path $BackupPath | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $BackendDir -Recurse -Force
    }

    Write-Log "Rollback completed successfully"

    # Restart
    Start-TapService
    Write-Log "=== Rollback complete ==="
}

# Main execution
Write-Log "=========================================="
Write-Log "TAP Update Script"
Write-Log "=========================================="

# Small delay to allow the calling process to begin shutdown
Start-Sleep -Seconds 3

try {
    if ($Rollback) {
        Restore-Backup
    } else {
        Apply-Update
    }
} catch {
    Write-Log "Fatal error: $_" "ERROR"
    Write-Log $_.ScriptStackTrace "ERROR"
    exit 1
}
