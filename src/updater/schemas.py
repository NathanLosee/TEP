"""Module defining schemas for updater-related operations."""

from pydantic import BaseModel


class ReleaseInfo(BaseModel):
    """Information about a GitHub release.

    Attributes:
        version (str): Parsed version string (e.g. "1.2.0").
        tag_name (str): Git tag name (e.g. "v1.2.0").
        published_at (str): ISO timestamp of the release.
        release_notes (str): Release body/changelog text.
        download_url (str): Direct download URL for the zip asset.
        asset_name (str): Filename of the zip asset.
        asset_size (int): Size of the asset in bytes.

    """

    version: str
    tag_name: str
    published_at: str
    release_notes: str
    download_url: str
    asset_name: str
    asset_size: int


class UpdateStatus(BaseModel):
    """Current state of the update system.

    Attributes:
        current_version (str): Running application version.
        latest_version (str | None): Latest available version.
        update_available (bool): Whether a newer version exists.
        last_checked (str | None): ISO timestamp of last check.
        download_progress (float | None): Download progress 0-100.
        downloaded_file (str | None): Path to downloaded file.
        state (str): Current state of the updater.
        error (str | None): Error message if state is error.
        backup_available (bool): Whether a rollback backup exists.

    """

    current_version: str
    latest_version: str | None = None
    update_available: bool = False
    last_checked: str | None = None
    download_progress: float | None = None
    downloaded_file: str | None = None
    state: str = "idle"
    error: str | None = None
    backup_available: bool = False
