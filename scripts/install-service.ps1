<#
.SYNOPSIS
    Install TEP as a Windows service using NSSM.

.DESCRIPTION
    This script downloads NSSM (if needed) and installs TEP as a Windows service
    that starts automatically on boot.

.PARAMETER InstallDir
    TEP installation directory. Default: C:\Program Files\TEP

.PARAMETER ServiceName
    Name for the Windows service. Default: TEPService

.PARAMETER Port
    Backend server port. Default: 8000

.PARAMETER Uninstall
    Remove the service instead of installing it.

.EXAMPLE
    .\install-service.ps1

.EXAMPLE
    .\install-service.ps1 -InstallDir "D:\TEP" -Port 8080

.EXAMPLE
    .\install-service.ps1 -Uninstall
#>

param(
    [string]$InstallDir = "C:\Program Files\TEP",
    [string]$ServiceName = "TEPService",
    [int]$Port = 8000,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# NSSM download URL and expected location
$NssmVersion = "2.24"
$NssmUrl = "https://nssm.cc/release/nssm-$NssmVersion.zip"
$NssmDir = Join-Path $InstallDir "nssm"
$NssmExe = Join-Path $NssmDir "win64\nssm.exe"

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    Write-Host "[TEP] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Status $Message "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-Status $Message "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-Status $Message "Red"
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-Nssm {
    if (Test-Path $NssmExe) {
        Write-Status "NSSM already installed at $NssmExe"
        return $true
    }

    Write-Status "Downloading NSSM $NssmVersion..."

    $zipPath = Join-Path $env:TEMP "nssm.zip"
    $extractPath = Join-Path $env:TEMP "nssm-extract"

    try {
        # Download NSSM
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $NssmUrl -OutFile $zipPath -UseBasicParsing

        # Extract
        if (Test-Path $extractPath) {
            Remove-Item $extractPath -Recurse -Force
        }
        Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

        # Copy to installation directory
        if (-not (Test-Path $NssmDir)) {
            New-Item -ItemType Directory -Path $NssmDir -Force | Out-Null
        }

        $sourcePath = Join-Path $extractPath "nssm-$NssmVersion"
        Copy-Item -Path "$sourcePath\*" -Destination $NssmDir -Recurse -Force

        # Cleanup
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue

        if (Test-Path $NssmExe) {
            Write-Success "NSSM installed successfully"
            return $true
        } else {
            Write-Error "NSSM installation failed - executable not found"
            return $false
        }
    }
    catch {
        Write-Error "Failed to download/install NSSM: $_"
        return $false
    }
}

function Install-TepService {
    $backendDir = Join-Path $InstallDir "backend"
    $executable = Join-Path $backendDir "tep.exe"
    $envFile = Join-Path $backendDir ".env"
    $logDir = Join-Path $InstallDir "logs"

    # Validate installation
    if (-not (Test-Path $executable)) {
        Write-Error "TEP executable not found at $executable"
        Write-Error "Please ensure TEP is properly installed."
        exit 1
    }

    # Create logs directory
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    # Check if service already exists
    $existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Warning "Service '$ServiceName' already exists. Stopping and removing..."
        & $NssmExe stop $ServiceName 2>$null
        & $NssmExe remove $ServiceName confirm 2>$null
        Start-Sleep -Seconds 2
    }

    Write-Status "Installing TEP as Windows service '$ServiceName'..."

    # Install service
    & $NssmExe install $ServiceName $executable
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install service"
        exit 1
    }

    # Configure service
    Write-Status "Configuring service..."

    # Set working directory
    & $NssmExe set $ServiceName AppDirectory $backendDir

    # Set display name and description
    & $NssmExe set $ServiceName DisplayName "TEP - Timeclock and Employee Payroll"
    & $NssmExe set $ServiceName Description "TEP backend server for timeclock and employee payroll management"

    # Set startup type to automatic
    & $NssmExe set $ServiceName Start SERVICE_AUTO_START

    # Configure stdout/stderr logging
    $stdoutLog = Join-Path $logDir "service-stdout.log"
    $stderrLog = Join-Path $logDir "service-stderr.log"
    & $NssmExe set $ServiceName AppStdout $stdoutLog
    & $NssmExe set $ServiceName AppStderr $stderrLog
    & $NssmExe set $ServiceName AppStdoutCreationDisposition 4
    & $NssmExe set $ServiceName AppStderrCreationDisposition 4
    & $NssmExe set $ServiceName AppRotateFiles 1
    & $NssmExe set $ServiceName AppRotateBytes 10485760

    # Configure restart on failure
    & $NssmExe set $ServiceName AppExit Default Restart
    & $NssmExe set $ServiceName AppRestartDelay 5000

    # Set environment variables if .env doesn't exist
    if (-not (Test-Path $envFile)) {
        Write-Warning ".env file not found. Creating default configuration..."
        $envContent = @"
ENVIRONMENT=production
LOG_LEVEL=INFO
BACKEND_PORT=$Port
ROOT_PASSWORD=ChangeThisPassword123!
DATABASE_URL=sqlite:///$InstallDir\data\tep.sqlite
"@
        $envContent | Out-File -FilePath $envFile -Encoding UTF8
        Write-Warning "Default .env created. IMPORTANT: Change ROOT_PASSWORD before starting!"
    }

    Write-Success "Service installed successfully!"
    Write-Status ""
    Write-Status "Service Management Commands:"
    Write-Status "  Start:   net start $ServiceName"
    Write-Status "  Stop:    net stop $ServiceName"
    Write-Status "  Status:  sc query $ServiceName"
    Write-Status ""
    Write-Status "Or use NSSM directly:"
    Write-Status "  $NssmExe start $ServiceName"
    Write-Status "  $NssmExe stop $ServiceName"
    Write-Status "  $NssmExe edit $ServiceName"
    Write-Status ""
    Write-Status "Logs are written to: $logDir"
}

function Uninstall-TepService {
    Write-Status "Removing TEP service..."

    # Check if NSSM exists
    if (-not (Test-Path $NssmExe)) {
        # Try to find nssm in PATH
        $nssm = Get-Command nssm -ErrorAction SilentlyContinue
        if ($nssm) {
            $NssmExe = $nssm.Path
        } else {
            Write-Warning "NSSM not found. Attempting to remove service using sc.exe..."

            $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
            if ($service) {
                if ($service.Status -eq "Running") {
                    Stop-Service -Name $ServiceName -Force
                    Start-Sleep -Seconds 2
                }
                sc.exe delete $ServiceName
            }
            return
        }
    }

    # Stop service if running
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq "Running") {
        Write-Status "Stopping service..."
        & $NssmExe stop $ServiceName
        Start-Sleep -Seconds 2
    }

    # Remove service
    if ($service) {
        Write-Status "Removing service..."
        & $NssmExe remove $ServiceName confirm
        Write-Success "Service removed successfully"
    } else {
        Write-Warning "Service '$ServiceName' not found"
    }
}

# Main execution
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  TEP Service Management Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check for administrator privileges
if (-not (Test-Administrator)) {
    Write-Error "This script requires administrator privileges."
    Write-Error "Please run PowerShell as Administrator and try again."
    exit 1
}

if ($Uninstall) {
    Uninstall-TepService
} else {
    # Download/verify NSSM
    if (-not (Get-Nssm)) {
        Write-Error "Cannot proceed without NSSM"
        exit 1
    }

    Install-TepService

    # Prompt to start service
    Write-Host ""
    $startNow = Read-Host "Start the service now? (Y/n)"
    if ($startNow -ne "n" -and $startNow -ne "N") {
        Write-Status "Starting service..."
        & $NssmExe start $ServiceName
        Start-Sleep -Seconds 3

        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Write-Success "Service is running!"
            Write-Status "Access TEP at: http://localhost:$Port"
        } else {
            Write-Warning "Service may not have started. Check logs at $InstallDir\logs"
        }
    }
}

Write-Host ""
