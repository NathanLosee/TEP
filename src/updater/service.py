"""Module providing core update logic for TAP self-updates."""

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Union

import httpx

from src.config import Settings
from src.logger.app_logger import get_logger
from src.logger.formatter import CustomFormatter
from src.updater.schemas import ReleaseInfo, UpdateStatus

formatter = CustomFormatter("%(asctime)s")
logger = get_logger(__name__, formatter)

_state_lock = Lock()
_state: dict = {
    "latest_version": None,
    "update_available": False,
    "last_checked": None,
    "download_progress": None,
    "downloaded_file": None,
    "state": "idle",
    "error": None,
}


def get_current_version() -> str:
    """Get the running application version.

    Returns:
        str: The current version string.

    """
    from src.main import app

    return app.version


def compare_versions(current: str, latest: str) -> int:
    """Compare two semver version strings.

    Args:
        current (str): Current version (e.g. "1.0.0").
        latest (str): Latest version (e.g. "1.2.0").

    Returns:
        int: -1 if current < latest, 0 if equal, 1 if current > latest.

    """
    def parse(v: str) -> list[int]:
        clean = v.lstrip("v")
        parts = clean.split(".")
        return [int(p) for p in parts[:3]]

    current_parts = parse(current)
    latest_parts = parse(latest)

    # Pad to 3 parts
    while len(current_parts) < 3:
        current_parts.append(0)
    while len(latest_parts) < 3:
        latest_parts.append(0)

    for c, l in zip(current_parts, latest_parts):
        if c < l:
            return -1
        if c > l:
            return 1
    return 0


def check_for_update(
    settings: Settings,
) -> Union[ReleaseInfo, None]:
    """Check GitHub Releases for a newer version.

    Args:
        settings (Settings): Application settings with GITHUB_REPO.

    Returns:
        Union[ReleaseInfo, None]: Release info if update available,
            None otherwise.

    Raises:
        ValueError: If GITHUB_REPO is not configured.

    """
    if not settings.GITHUB_REPO:
        raise ValueError("GITHUB_REPO is not configured")

    with _state_lock:
        _state["state"] = "checking"
        _state["error"] = None

    try:
        headers = {"Accept": "application/vnd.github+json"}
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

        url = (
            f"https://api.github.com/repos/"
            f"{settings.GITHUB_REPO}/releases/latest"
        )

        response = httpx.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        tag_name = data.get("tag_name", "")
        version = tag_name.lstrip("v")
        current = get_current_version()

        # Find zip asset matching TAP-*.zip
        zip_asset = None
        for asset in data.get("assets", []):
            name = asset.get("name", "")
            if name.startswith("TAP-") and name.endswith(".zip"):
                zip_asset = asset
                break

        now = datetime.now(timezone.utc).isoformat()

        with _state_lock:
            _state["last_checked"] = now
            _state["state"] = "idle"

        if not zip_asset:
            logger.warning(
                f"No TAP-*.zip asset found in release {tag_name}"
            )
            with _state_lock:
                _state["update_available"] = False
                _state["latest_version"] = version
            return None

        if compare_versions(current, version) >= 0:
            with _state_lock:
                _state["update_available"] = False
                _state["latest_version"] = version
            return None

        release_info = ReleaseInfo(
            version=version,
            tag_name=tag_name,
            published_at=data.get("published_at", ""),
            release_notes=data.get("body", ""),
            download_url=zip_asset["browser_download_url"],
            asset_name=zip_asset["name"],
            asset_size=zip_asset["size"],
        )

        with _state_lock:
            _state["update_available"] = True
            _state["latest_version"] = version

        logger.info(
            f"Update available: {current} -> {version}"
        )
        return release_info

    except Exception as e:
        logger.error(f"Failed to check for updates: {e}")
        with _state_lock:
            _state["state"] = "error"
            _state["error"] = str(e)
        raise


def download_update(
    release_info: ReleaseInfo,
    settings: Settings,
) -> str:
    """Download an update asset from GitHub.

    Args:
        release_info (ReleaseInfo): Release info with download URL.
        settings (Settings): Application settings.

    Returns:
        str: Path to the downloaded file.

    Raises:
        RuntimeError: If a download is already in progress.

    """
    with _state_lock:
        if _state["state"] == "downloading":
            raise RuntimeError("Download already in progress")
        _state["state"] = "downloading"
        _state["download_progress"] = 0.0
        _state["error"] = None

    try:
        # Determine download directory
        if getattr(sys, "frozen", False):
            download_dir = Path(sys.executable).parent / "updates"
        else:
            download_dir = Path("updates")
        download_dir.mkdir(parents=True, exist_ok=True)

        download_path = download_dir / release_info.asset_name

        headers = {"Accept": "application/octet-stream"}
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

        with httpx.stream(
            "GET",
            release_info.download_url,
            headers=headers,
            follow_redirects=True,
            timeout=300,
        ) as response:
            response.raise_for_status()
            total = release_info.asset_size
            downloaded = 0

            with open(download_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=65536):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        progress = (downloaded / total) * 100
                        with _state_lock:
                            _state["download_progress"] = round(
                                progress, 1
                            )

        file_path = str(download_path)
        with _state_lock:
            _state["state"] = "ready"
            _state["download_progress"] = 100.0
            _state["downloaded_file"] = file_path

        logger.info(
            f"Update downloaded: {release_info.asset_name}"
        )
        return file_path

    except Exception as e:
        logger.error(f"Download failed: {e}")
        with _state_lock:
            _state["state"] = "error"
            _state["error"] = str(e)
            _state["download_progress"] = None
        raise


def get_apply_script_path() -> Path:
    """Get the path to the apply-update PowerShell script.

    Returns:
        Path: Absolute path to apply-update.ps1.

    """
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent.parent

    return base / "scripts" / "apply-update.ps1"


def get_backup_path() -> Union[Path, None]:
    """Find the most recent backup directory.

    Returns:
        Union[Path, None]: Path to backup directory, or None.

    """
    if getattr(sys, "frozen", False):
        parent = Path(sys.executable).parent.parent
    else:
        parent = Path(__file__).parent.parent.parent

    backups = sorted(
        parent.glob("backend-backup-*"),
        reverse=True,
    )
    return backups[0] if backups else None


def apply_update() -> None:
    """Apply a downloaded update by launching the helper script.

    The helper script waits for the current process to exit, then
    replaces the backend files and restarts the service.

    Raises:
        RuntimeError: If not running as frozen exe or no download ready.
        FileNotFoundError: If the apply script is missing.

    """
    if not getattr(sys, "frozen", False):
        raise RuntimeError(
            "Updates can only be applied to packaged deployments"
        )

    with _state_lock:
        downloaded = _state.get("downloaded_file")
        if not downloaded or _state["state"] != "ready":
            raise RuntimeError("No downloaded update ready to apply")
        _state["state"] = "applying"

    script_path = get_apply_script_path()
    if not script_path.exists():
        with _state_lock:
            _state["state"] = "error"
            _state["error"] = "apply-update.ps1 not found"
        raise FileNotFoundError(
            f"Apply script not found: {script_path}"
        )

    backend_dir = str(Path(sys.executable).parent)

    # Launch PowerShell as a detached process
    cmd = [
        "powershell.exe",
        "-ExecutionPolicy", "Bypass",
        "-File", str(script_path),
        "-BackendDir", backend_dir,
        "-UpdateZip", downloaded,
    ]

    logger.info(f"Launching update apply script: {cmd}")

    # CREATE_NEW_PROCESS_GROUP + DETACHED_PROCESS on Windows
    creation_flags = (
        subprocess.CREATE_NEW_PROCESS_GROUP
        | subprocess.DETACHED_PROCESS
    )
    subprocess.Popen(
        cmd,
        creationflags=creation_flags,
        close_fds=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # The app should be shut down after this call returns.
    # The route handler will trigger a graceful shutdown.


def rollback() -> None:
    """Rollback to the previous version using the backup.

    Raises:
        RuntimeError: If not running as frozen exe or no backup exists.
        FileNotFoundError: If the apply script is missing.

    """
    if not getattr(sys, "frozen", False):
        raise RuntimeError(
            "Rollback can only be performed on packaged deployments"
        )

    backup = get_backup_path()
    if not backup:
        raise RuntimeError("No backup available for rollback")

    script_path = get_apply_script_path()
    if not script_path.exists():
        raise FileNotFoundError(
            f"Apply script not found: {script_path}"
        )

    backend_dir = str(Path(sys.executable).parent)

    cmd = [
        "powershell.exe",
        "-ExecutionPolicy", "Bypass",
        "-File", str(script_path),
        "-BackendDir", backend_dir,
        "-Rollback",
        "-BackupDir", str(backup),
    ]

    logger.info(f"Launching rollback script: {cmd}")

    creation_flags = (
        subprocess.CREATE_NEW_PROCESS_GROUP
        | subprocess.DETACHED_PROCESS
    )
    subprocess.Popen(
        cmd,
        creationflags=creation_flags,
        close_fds=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def get_status() -> UpdateStatus:
    """Get the current update status.

    Returns:
        UpdateStatus: Current state of the updater.

    """
    with _state_lock:
        return UpdateStatus(
            current_version=get_current_version(),
            latest_version=_state["latest_version"],
            update_available=_state["update_available"],
            last_checked=_state["last_checked"],
            download_progress=_state["download_progress"],
            downloaded_file=_state["downloaded_file"],
            state=_state["state"],
            error=_state["error"],
            backup_available=get_backup_path() is not None,
        )


def reset_state() -> None:
    """Reset the updater state to idle. Used for testing."""
    with _state_lock:
        _state["latest_version"] = None
        _state["update_available"] = False
        _state["last_checked"] = None
        _state["download_progress"] = None
        _state["downloaded_file"] = None
        _state["state"] = "idle"
        _state["error"] = None
