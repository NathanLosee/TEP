"""API routes for system settings operations."""

from fastapi import APIRouter, Depends, File, Security, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.services import requires_license, requires_permission, validate
from src.system_settings.constants import (
    ALLOWED_LOGO_TYPES,
    BASE_URL,
    EXC_MSG_INVALID_LOGO_TYPE,
    EXC_MSG_LOGO_TOO_LARGE,
    MAX_LOGO_SIZE,
)
from src.system_settings.repository import (
    delete_logo,
    get_logo,
    get_settings,
    update_logo,
    update_settings,
)
from src.system_settings.schemas import SystemSettingsResponse, SystemSettingsUpdate

router = APIRouter(prefix=BASE_URL, tags=["system-settings"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SystemSettingsResponse,
)
def get_system_settings(
    db: Session = Depends(get_db),
):
    """Get current system settings.

    This endpoint is publicly accessible so the frontend can load
    theme settings before authentication.

    Args:
        db: Database session.

    Returns:
        SystemSettingsResponse: Current system settings.

    """
    settings = get_settings(db)
    return SystemSettingsResponse(
        id=settings.id,
        primary_color=settings.primary_color,
        secondary_color=settings.secondary_color,
        accent_color=settings.accent_color,
        company_name=settings.company_name,
        has_logo=settings.logo_data is not None,
        logo_filename=settings.logo_filename,
    )


@router.put(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SystemSettingsResponse,
)
def update_system_settings(
    request: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.update"]  # Admin permission
    ),
    _: None = Depends(requires_license),
):
    """Update system settings (colors, company name).

    Args:
        request: Update request data.
        db: Database session.
        caller_badge: Badge number of the caller (for audit).

    Returns:
        SystemSettingsResponse: Updated system settings.

    """
    settings = get_settings(db)
    updated = update_settings(settings, request, db)
    return SystemSettingsResponse(
        id=updated.id,
        primary_color=updated.primary_color,
        secondary_color=updated.secondary_color,
        accent_color=updated.accent_color,
        company_name=updated.company_name,
        has_logo=updated.logo_data is not None,
        logo_filename=updated.logo_filename,
    )


@router.post(
    "/logo",
    status_code=status.HTTP_200_OK,
    response_model=SystemSettingsResponse,
)
async def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.update"]  # Admin permission
    ),
    _: None = Depends(requires_license),
):
    """Upload a new logo image.

    Args:
        file: The logo file to upload.
        db: Database session.
        caller_badge: Badge number of the caller (for audit).

    Returns:
        SystemSettingsResponse: Updated system settings.

    Raises:
        400: If file type is invalid or file is too large.

    """
    # Validate file type
    validate(
        file.content_type in ALLOWED_LOGO_TYPES,
        EXC_MSG_INVALID_LOGO_TYPE,
        status.HTTP_400_BAD_REQUEST,
    )

    # Read file content
    content = await file.read()

    # Validate file size
    validate(
        len(content) <= MAX_LOGO_SIZE,
        EXC_MSG_LOGO_TOO_LARGE,
        status.HTTP_400_BAD_REQUEST,
    )

    settings = get_settings(db)
    updated = update_logo(
        settings,
        logo_data=content,
        mime_type=file.content_type,
        filename=file.filename,
        db=db,
    )

    return SystemSettingsResponse(
        id=updated.id,
        primary_color=updated.primary_color,
        secondary_color=updated.secondary_color,
        accent_color=updated.accent_color,
        company_name=updated.company_name,
        has_logo=updated.logo_data is not None,
        logo_filename=updated.logo_filename,
    )


@router.get(
    "/logo",
    status_code=status.HTTP_200_OK,
)
def get_logo_image(
    db: Session = Depends(get_db),
):
    """Get the logo image file.

    This endpoint is publicly accessible so the frontend can display
    the logo without authentication.

    Args:
        db: Database session.

    Returns:
        Response: Logo image file or 204 if no logo exists.

    """
    logo = get_logo(db)
    if logo:
        logo_data, mime_type, filename = logo
        return Response(
            content=logo_data,
            media_type=mime_type,
            headers={"Content-Disposition": f'inline; filename="{filename}"'},
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/logo",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_logo_image(
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.update"]  # Admin permission
    ),
    _: None = Depends(requires_license),
):
    """Delete the logo image.

    Args:
        db: Database session.
        caller_badge: Badge number of the caller (for audit).

    """
    settings = get_settings(db)
    delete_logo(settings, db)
