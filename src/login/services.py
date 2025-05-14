"""Module providing the business logic for login-related operations."""

from datetime import datetime, timedelta, timezone
import os
from typing import Annotated, Optional
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
import jwt
import bcrypt
from src.constants import RESOURCE_SCOPES
from src.employee.models import Employee
from src.login.constants import (
    EXC_MSG_LOGIN_FAILED,
    EXC_MSG_REFRESH_TOKEN_NOT_FOUND,
    EXC_MSG_REFRESH_TOKEN_INVALID,
    EXC_MSG_REFRESH_TOKEN_EXPIRED,
    EXC_MSG_MISSING_PERMISSION,
)


rsa_private_key: rsa.RSAPrivateKey = None
rsa_public_key: rsa.RSAPublicKey = None
signing_bytes: bytes = None
verifying_bytes: bytes = None

algorithm = "RS256"
access_exp_time = 15
refresh_exp_time = 60 * 24  # 1 day
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", scopes=RESOURCE_SCOPES)


def load_keys():
    """Load the RSA private and public keys from local file."""
    global rsa_private_key, rsa_public_key, signing_bytes, verifying_bytes

    if not os.path.exists("rsa_private_key.pem"):
        rsa_private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        with open("rsa_private_key.pem", "wb") as private_key_file:
            private_key_file.write(
                rsa_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
    else:
        with open("rsa_private_key.pem", "rb") as private_key_file:
            rsa_private_key = serialization.load_pem_private_key(
                private_key_file.read(), password=None
            )
    rsa_public_key = rsa_private_key.public_key()

    signing_bytes = rsa_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    verifying_bytes = rsa_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def hash_password(password: str) -> str:
    """Hash the provided password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.

    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the provided password against the hashed password.

    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to check against.

    Returns:
        bool: True if the passwords match, False otherwise.

    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_expiration_time(access_exp: bool) -> datetime:
    """Get the expiration time for the token.

    Args:
        access_exp (bool): Whether to get the expiration time for access token.

    Returns:
        datetime: The expiration time.

    """
    if access_exp:
        return datetime.now(timezone.utc) + timedelta(minutes=access_exp_time)
    else:
        return datetime.now(timezone.utc) + timedelta(minutes=refresh_exp_time)


def encode_jwt_token(payload: dict) -> str:
    """Encode the provided payload into a JWT token.

    Args:
        payload (dict): The payload to encode.

    Returns:
        str: The JWT token.

    """
    return jwt.encode(payload, key=signing_bytes, algorithm="RS256")


def decode_jwt_token(token: str) -> dict:
    """Decode the provided JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded payload.

    """
    try:
        payload = jwt.decode(token, key=verifying_bytes, algorithms=["RS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_REFRESH_TOKEN_EXPIRED,
        )
    return payload


def requires_permission(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> int:
    """Check if the user has the required permission.

    Args:
        jwt (str): The JWT token to check.
        resource (str): The resource to check.

    Returns:
        int: The employee ID if the permission is granted.

    """
    payload = decode_jwt_token(token)
    token_scopes = payload.get("scopes", [])
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=EXC_MSG_MISSING_PERMISSION,
            )
    return int(payload.get("sub"))


def validate_login(
    login_successful: bool,
) -> Optional[bool]:
    """Validate whether login succeeded.

    Args:
        login_successful (bool): Whether the login was successful.

    Returns:
        bool: True if credentials are valid

    """
    if login_successful:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_LOGIN_FAILED,
        )


def verify_refresh_token_exists(
    refresh_token: str | None,
) -> bool:
    """Check if the refresh token exists.

    Args:
        refresh_token (str | None): The refresh token to check.

    Returns:
        bool: True if the refresh token exists.

    """
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_REFRESH_TOKEN_NOT_FOUND,
        )
    return True


def verify_username_exists(
    username: str | None,
) -> bool:
    """Check if the username exists.

    Args:
        username (str | None): The username to check.

    Returns:
        bool: True if the username exists.

    """
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_REFRESH_TOKEN_INVALID,
        )
    return True


def generate_permission_list(employee: Employee) -> list[str]:
    """Generate permission list for the logged-in user.

    Args:
        employee (Employee): The employee object containing user credentials.

    Returns:
        list[str]: A list of unique permissions for the user.

    """
    permissions_set = set()
    for role in employee.auth_roles:
        for permission in role.permissions:
            permissions_set.add(permission.resource)
    return list(permissions_set)
