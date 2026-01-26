"""TEP License Server - FastAPI application for license management.

This server handles:
- Creating new licenses
- Activating licenses for specific machines
- Validating existing activations
- Deactivating licenses
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db
from key_generator import (
    generate_activation_key,
    generate_unique_license_key,
    normalize_license_key,
    validate_license_key_format,
    verify_activation_key,
)
from models import Activation, License
from schemas import (
    ActivationRequest,
    ActivationResponse,
    DeactivationRequest,
    LicenseCreate,
    LicenseResponse,
    LicenseStatusResponse,
    ValidationRequest,
    ValidationResponse,
)

# Load private key for signing activations
PRIVATE_KEY_PATH = Path(__file__).parent / "private_key.pem"


def load_private_key() -> Optional[bytes]:
    """Load the private key from file if it exists."""
    if PRIVATE_KEY_PATH.exists():
        return PRIVATE_KEY_PATH.read_bytes()
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Initialize database on startup
    init_db()
    print("License Server started")
    print(f"Private key available: {PRIVATE_KEY_PATH.exists()}")
    yield
    print("License Server shutting down")


app = FastAPI(
    title="TEP License Server",
    description="License management server for TEP Time Entry Portal",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow CORS for the main application to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Admin Endpoints (for managing licenses)
# ============================================================================


@app.post(
    "/api/licenses",
    status_code=status.HTTP_201_CREATED,
    response_model=LicenseResponse,
    tags=["admin"],
)
def create_license(
    request: LicenseCreate,
    db: Session = Depends(get_db),
):
    """Create a new license.

    Generates a unique license key that can be given to a customer.
    The license must be activated on a specific machine before use.
    """
    private_key = load_private_key()
    if not private_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Private key not configured. Run 'python license_tool.py generate-keys' first.",
        )

    # Generate unique license key
    license_key = generate_unique_license_key(word_format=False)

    # Create license record
    license_obj = License(
        license_key=license_key,
        customer_name=request.customer_name,
        notes=request.notes,
        is_active=True,
    )
    db.add(license_obj)
    db.commit()
    db.refresh(license_obj)

    return license_obj


@app.get(
    "/api/licenses",
    response_model=list[LicenseResponse],
    tags=["admin"],
)
def list_licenses(
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    """List all licenses."""
    query = db.query(License)
    if active_only:
        query = query.filter(License.is_active == True)
    return query.all()


@app.get(
    "/api/licenses/{license_id}",
    response_model=LicenseResponse,
    tags=["admin"],
)
def get_license(
    license_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific license by ID."""
    license_obj = db.query(License).filter(License.id == license_id).first()
    if not license_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found",
        )
    return license_obj


@app.delete(
    "/api/licenses/{license_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["admin"],
)
def revoke_license(
    license_id: int,
    db: Session = Depends(get_db),
):
    """Revoke a license (deactivate it and all its activations)."""
    license_obj = db.query(License).filter(License.id == license_id).first()
    if not license_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found",
        )

    # Deactivate the license
    license_obj.is_active = False

    # Deactivate all activations for this license
    db.query(Activation).filter(
        Activation.license_id == license_id,
        Activation.is_active == True,
    ).update({"is_active": False, "deactivated_at": datetime.utcnow()})

    db.commit()


# ============================================================================
# Client Endpoints (called by the main TEP application)
# ============================================================================


@app.post(
    "/api/activate",
    status_code=status.HTTP_200_OK,
    response_model=ActivationResponse,
    tags=["client"],
)
def activate_license(
    request: ActivationRequest,
    db: Session = Depends(get_db),
):
    """Activate a license for a specific machine.

    Called by the client application when a user enters a license key.
    Returns an activation_key that proves the license is valid for this machine.
    """
    private_key = load_private_key()
    if not private_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="License server not configured",
        )

    # Validate license key format
    if not validate_license_key_format(request.license_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid license key format",
        )

    # Normalize the license key to hex format for storage/lookup
    normalized_key = normalize_license_key(request.license_key)

    # Find the license
    license_obj = db.query(License).filter(
        License.license_key == normalized_key
    ).first()

    if not license_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License key not found",
        )

    if not license_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="License has been revoked",
        )

    # Check if this machine is already activated for this license
    existing_activation = db.query(Activation).filter(
        Activation.license_id == license_obj.id,
        Activation.machine_id == request.machine_id,
        Activation.is_active == True,
    ).first()

    if existing_activation:
        # Return existing activation
        return ActivationResponse(
            license_key=normalized_key,
            activation_key=existing_activation.activation_key,
            activated_at=existing_activation.activated_at,
        )

    # Generate activation key (sign license_key + machine_id)
    activation_key = generate_activation_key(
        private_key,
        normalized_key,
        request.machine_id,
    )

    # Store the activation
    activation = Activation(
        license_id=license_obj.id,
        machine_id=request.machine_id,
        activation_key=activation_key,
        is_active=True,
    )
    db.add(activation)
    db.commit()
    db.refresh(activation)

    return ActivationResponse(
        license_key=normalized_key,
        activation_key=activation_key,
        activated_at=activation.activated_at,
    )


@app.post(
    "/api/validate",
    response_model=ValidationResponse,
    tags=["client"],
)
def validate_activation(
    request: ValidationRequest,
    db: Session = Depends(get_db),
):
    """Validate an existing activation.

    Called by the client application on startup to verify the stored
    activation is still valid.
    """
    # Normalize the license key
    try:
        normalized_key = normalize_license_key(request.license_key)
    except ValueError:
        return ValidationResponse(
            is_valid=False,
            message="Invalid license key format",
        )

    # Check if the license exists and is active
    license_obj = db.query(License).filter(
        License.license_key == normalized_key
    ).first()

    if not license_obj:
        return ValidationResponse(
            is_valid=False,
            message="License not found",
        )

    if not license_obj.is_active:
        return ValidationResponse(
            is_valid=False,
            message="License has been revoked",
        )

    # Check if the activation exists and is active
    activation = db.query(Activation).filter(
        Activation.license_id == license_obj.id,
        Activation.machine_id == request.machine_id,
        Activation.is_active == True,
    ).first()

    if not activation:
        return ValidationResponse(
            is_valid=False,
            message="No activation found for this machine",
        )

    # Verify the activation key cryptographically
    is_valid = verify_activation_key(
        normalized_key,
        request.machine_id,
        request.activation_key,
    )

    if not is_valid:
        return ValidationResponse(
            is_valid=False,
            message="Invalid activation key",
        )

    return ValidationResponse(
        is_valid=True,
        message="License is valid",
    )


@app.post(
    "/api/deactivate",
    status_code=status.HTTP_200_OK,
    response_model=ValidationResponse,
    tags=["client"],
)
def deactivate_machine(
    request: DeactivationRequest,
    db: Session = Depends(get_db),
):
    """Deactivate a license for a specific machine.

    Called when a user wants to transfer their license to a different machine.
    """
    # Normalize the license key
    try:
        normalized_key = normalize_license_key(request.license_key)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid license key format",
        )

    # Find the license
    license_obj = db.query(License).filter(
        License.license_key == normalized_key
    ).first()

    if not license_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found",
        )

    # Find and deactivate the activation
    activation = db.query(Activation).filter(
        Activation.license_id == license_obj.id,
        Activation.machine_id == request.machine_id,
        Activation.is_active == True,
    ).first()

    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active activation found for this machine",
        )

    activation.is_active = False
    activation.deactivated_at = datetime.utcnow()
    db.commit()

    return ValidationResponse(
        is_valid=True,
        message="License deactivated for this machine",
    )


@app.get(
    "/api/status",
    response_model=LicenseStatusResponse,
    tags=["client"],
)
def check_license_status(
    license_key: str,
    machine_id: str,
    db: Session = Depends(get_db),
):
    """Check the status of a license for a specific machine.

    Quick endpoint to check if a license is valid without full validation.
    """
    try:
        normalized_key = normalize_license_key(license_key)
    except ValueError:
        return LicenseStatusResponse(
            is_valid=False,
            message="Invalid license key format",
        )

    # Check if the license exists and is active
    license_obj = db.query(License).filter(
        License.license_key == normalized_key
    ).first()

    if not license_obj or not license_obj.is_active:
        return LicenseStatusResponse(
            is_valid=False,
            message="License not found or revoked",
        )

    # Check for active activation
    activation = db.query(Activation).filter(
        Activation.license_id == license_obj.id,
        Activation.machine_id == machine_id,
        Activation.is_active == True,
    ).first()

    if activation:
        return LicenseStatusResponse(
            is_valid=True,
            license_key=normalized_key,
            activated_at=activation.activated_at,
            message="License is active",
        )

    return LicenseStatusResponse(
        is_valid=False,
        license_key=normalized_key,
        message="License exists but not activated for this machine",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
