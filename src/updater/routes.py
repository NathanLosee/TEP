"""Module defining API for updater-related operations."""

import os
import signal
import sys

from fastapi import APIRouter, Depends, Security, status
from fastapi.responses import JSONResponse

from src.config import Settings
from src.services import (
    create_event_log,
    requires_license,
    requires_permission,
    validate,
)
from src.updater.constants import (
    BASE_URL,
    EXC_MSG_DOWNLOAD_IN_PROGRESS,
    EXC_MSG_NO_BACKUP,
    EXC_MSG_NO_DOWNLOAD_READY,
    EXC_MSG_NO_UPDATE_AVAILABLE,
    EXC_MSG_NOT_CONFIGURED,
    EXC_MSG_NOT_FROZEN,
    IDENTIFIER,
)
from src.updater.schemas import ReleaseInfo, UpdateStatus
from src.updater.service import (
    apply_update,
    check_for_update,
    download_update,
    get_backup_path,
    get_status,
    rollback,
)

router = APIRouter(prefix=BASE_URL, tags=["updater"])


def _get_settings() -> Settings:
    return Settings()


@router.get(
    "/check",
    status_code=status.HTTP_200_OK,
    response_model=ReleaseInfo,
)
def check_for_updates(
    settings: Settings = Depends(_get_settings),
    caller_badge: str = Security(
        requires_permission, scopes=["system.update"]
    ),
    _: None = Depends(requires_license),
):
    """Check GitHub for available updates.

    Args:
        settings (Settings): Application settings.
        caller_badge (str): Badge of the calling user.

    Returns:
        ReleaseInfo: Information about the available update.

    """
    validate(
        settings.GITHUB_REPO,
        EXC_MSG_NOT_CONFIGURED,
        status.HTTP_400_BAD_REQUEST,
    )

    release_info = check_for_update(settings)
    validate(
        release_info is not None,
        EXC_MSG_NO_UPDATE_AVAILABLE,
        status.HTTP_204_NO_CONTENT,
    )

    return release_info


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    response_model=UpdateStatus,
)
def get_update_status(
    caller_badge: str = Security(
        requires_permission, scopes=["system.update"]
    ),
    _: None = Depends(requires_license),
):
    """Get the current update status.

    Returns:
        UpdateStatus: Current state of the updater.

    """
    return get_status()


@router.post(
    "/download",
    status_code=status.HTTP_202_ACCEPTED,
)
def download_latest_update(
    settings: Settings = Depends(_get_settings),
    caller_badge: str = Security(
        requires_permission, scopes=["system.update"]
    ),
    _: None = Depends(requires_license),
):
    """Download the latest available update.

    Args:
        settings (Settings): Application settings.
        caller_badge (str): Badge of the calling user.

    Returns:
        dict: Status message with download path.

    """
    validate(
        settings.GITHUB_REPO,
        EXC_MSG_NOT_CONFIGURED,
        status.HTTP_400_BAD_REQUEST,
    )

    current_status = get_status()
    validate(
        current_status.state != "downloading",
        EXC_MSG_DOWNLOAD_IN_PROGRESS,
        status.HTTP_409_CONFLICT,
    )

    release_info = check_for_update(settings)
    validate(
        release_info is not None,
        EXC_MSG_NO_UPDATE_AVAILABLE,
        status.HTTP_404_NOT_FOUND,
    )

    file_path = download_update(release_info, settings)

    return {
        "status": "downloaded",
        "file": file_path,
        "version": release_info.version,
    }


@router.post(
    "/apply",
    status_code=status.HTTP_200_OK,
)
def apply_downloaded_update(
    caller_badge: str = Security(
        requires_permission, scopes=["system.update"]
    ),
    _: None = Depends(requires_license),
):
    """Apply a previously downloaded update.

    This triggers a graceful shutdown. The PowerShell helper script
    replaces the backend files and restarts the service.

    Args:
        caller_badge (str): Badge of the calling user.

    Returns:
        dict: Status message.

    """
    validate(
        getattr(sys, "frozen", False),
        EXC_MSG_NOT_FROZEN,
        status.HTTP_400_BAD_REQUEST,
    )

    current_status = get_status()
    validate(
        current_status.state == "ready" and current_status.downloaded_file,
        EXC_MSG_NO_DOWNLOAD_READY,
        status.HTTP_400_BAD_REQUEST,
    )

    apply_update()

    # Schedule graceful shutdown
    os.kill(os.getpid(), signal.SIGTERM)

    return {
        "status": "applying",
        "message": "Update is being applied. The server will restart.",
    }


@router.post(
    "/rollback",
    status_code=status.HTTP_200_OK,
)
def rollback_update(
    caller_badge: str = Security(
        requires_permission, scopes=["system.update"]
    ),
    _: None = Depends(requires_license),
):
    """Rollback to the previous version using the backup.

    Args:
        caller_badge (str): Badge of the calling user.

    Returns:
        dict: Status message.

    """
    validate(
        getattr(sys, "frozen", False),
        EXC_MSG_NOT_FROZEN,
        status.HTTP_400_BAD_REQUEST,
    )

    validate(
        get_backup_path() is not None,
        EXC_MSG_NO_BACKUP,
        status.HTTP_400_BAD_REQUEST,
    )

    rollback()

    # Schedule graceful shutdown
    os.kill(os.getpid(), signal.SIGTERM)

    return {
        "status": "rolling_back",
        "message": "Rollback in progress. The server will restart.",
    }
