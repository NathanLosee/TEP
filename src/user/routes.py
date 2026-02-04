"""Module defining API for user-related operations."""

import jwt
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    Security,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth_role.schemas import AuthRoleExtended
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.config import settings
import src.services as services
from src.services import (
    algorithm,
    create_event_log,
    generate_access_token,
    generate_refresh_token,
    requires_license,
    requires_permission,
    validate,
    verify_password,
)
from src.user.constants import (
    BASE_URL,
    EXC_MSG_ACCESS_TOKEN_NOT_FOUND,
    EXC_MSG_LOGIN_FAILED,
    EXC_MSG_REFRESH_TOKEN_INVALID,
    EXC_MSG_REFRESH_TOKEN_NOT_FOUND,
    EXC_MSG_USER_NOT_FOUND,
    EXC_MSG_USER_WITH_ID_EXISTS,
    EXC_MSG_WRONG_PASSWORD,
    IDENTIFIER,
    MSG_LOGOUT_SUCCESS,
)
from src.user.repository import (
    clean_invalidated_tokens,
    create_user as create_user_in_db,
    delete_user as delete_user_from_db,
    get_invalidated_tokens,
    get_user_by_badge_number as get_user_by_badge_number_from_db,
    get_user_by_id as get_user_by_id_from_db,
    get_users as get_users_from_db,
    invalidate_token,
    update_user as update_user_in_db,
)
from src.user.schemas import UserBase, UserPasswordChange, UserResponse

router = APIRouter(prefix=BASE_URL, tags=["user"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
def create_user(
    request: UserBase,
    db: Session = Depends(get_db),
    caller_badge: str = Security(requires_permission, scopes=["user.create"]),
    _: None = Depends(requires_license),
):
    """Insert new user data.

    Args:
        request (UserBase): Request data for new user.
        db (Session, optional): Database session for current request.

    Returns:
        UserResponse: The created user.

    """
    duplicate_user = get_user_by_badge_number_from_db(request.badge_number, db)
    validate(
        duplicate_user is None,
        EXC_MSG_USER_WITH_ID_EXISTS,
        status.HTTP_409_CONFLICT,
        field="badge_number",
        constraint="unique",
    )

    user = create_user_in_db(request, db)
    log_args = {"badge_number": user.badge_number}
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_badge, db)
    return user


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    caller_badge: str = Security(requires_permission, scopes=["user.read"]),
):
    """Retrieve all existing users.

    Args:
        db (Session, optional): Database session for current request.

    Returns:
        list[UserResponse]: The retrieved users.

    """
    return get_users_from_db(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(requires_permission, scopes=["user.read"]),
):
    """Retrieve a user by a provided id.

    Args:
        id (int): User's unique identifier.
        db (Session, optional): Database session for current request.

    Returns:
        UserResponse: The user with the provided id.

    """
    user = get_user_by_id_from_db(id, db)
    validate(
        user,
        EXC_MSG_USER_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    return user


@router.get(
    "/{id}/auth_roles",
    status_code=status.HTTP_200_OK,
    response_model=list[AuthRoleExtended],
)
def get_user_auth_roles(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(requires_permission, scopes=["user.read"]),
):
    """Retrieve a user's auth roles by a provided id.

    Args:
        id (int): User's unique identifier.
        db (Session, optional): Database session for current request.

    Returns:
        list[AuthRoleExtended]: The user's auth roles.

    """
    user = get_user_by_id_from_db(id, db)
    validate(
        user,
        EXC_MSG_USER_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    return user.auth_roles


@router.put(
    "/{badge_number}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
def update_user_password(
    badge_number: str,
    request: UserPasswordChange,
    db: Session = Depends(get_db),
    caller_badge: str = Security(requires_permission, scopes=[]),
    _: None = Depends(requires_license),
):
    """Update a user's password.

    Users can change their own password (requires current password).
    Users with user.update permission can change any user's
    password (no current password needed).

    Args:
        badge_number (str): User's badge number.
        request (UserPasswordChange): Request data for updating user.
        db (Session, optional): Database session for current request.
        caller_badge (str): Badge number of the authenticated caller.

    Returns:
        UserResponse: The updated user.

    """
    validate(
        request.badge_number == badge_number,
        EXC_MSG_IDS_DO_NOT_MATCH,
        status.HTTP_400_BAD_REQUEST,
    )

    user = get_user_by_badge_number_from_db(badge_number, db)
    validate(
        user,
        EXC_MSG_USER_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    # Check if user is changing their own password or has admin permission
    is_self_update = caller_badge == badge_number
    caller_user = get_user_by_badge_number_from_db(caller_badge, db)
    has_admin_permission = any(
        "user.update" in [perm.resource for perm in role.permissions]
        for role in caller_user.auth_roles
    )

    # If user is changing their own password, verify current password
    if is_self_update and not has_admin_permission:
        validate(
            verify_password(request.password, user.password),
            EXC_MSG_WRONG_PASSWORD,
            status.HTTP_403_FORBIDDEN,
        )
    # If user has admin permission, they can change without current password
    elif not has_admin_permission:
        # User doesn't have permission to change other users' passwords
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You don't have permission to "
                "change other users' passwords"
            ),
        )

    user = update_user_in_db(
        user,
        UserBase(badge_number=badge_number, password=request.new_password),
        db,
    )
    log_args = {
        "badge_number": user.badge_number,
        "changed_by": caller_badge,
        "is_self_update": is_self_update,
    }
    create_event_log(IDENTIFIER, "UPDATE_PASSWORD", log_args, caller_badge, db)
    return user


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(requires_permission, scopes=["user.delete"]),
    _: None = Depends(requires_license),
):
    """Delete a user by a provided id.

    Args:
        id (int): User's unique identifier.
        db (Session, optional): Database session for current request.

    """
    user = get_user_by_id_from_db(id, db)
    validate(
        user,
        EXC_MSG_USER_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    delete_user_from_db(user, db)
    log_args = {"badge_number": user.badge_number}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
def login(
    response: Response,
    login: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Handle user login.

    Args:
        login (OAuth2PasswordRequestForm): Login data provided by the user.
        db (Session, optional): Database session for current request.

    Returns:
        dict: Access token and token type.

    """
    user = get_user_by_badge_number_from_db(login.username, db)
    validate(
        user,
        EXC_MSG_LOGIN_FAILED,
        status.HTTP_401_UNAUTHORIZED,
    )
    validate(
        verify_password(login.password, user.password),
        EXC_MSG_LOGIN_FAILED,
        status.HTTP_401_UNAUTHORIZED,
    )

    clean_invalidated_tokens(db)

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRY_MINUTES * 60,
    )
    log_args = {"badge_number": user.badge_number}
    create_event_log(IDENTIFIER, "LOGIN", log_args, user.badge_number, db)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    request: Request,
    db: Session = Depends(get_db),
):
    """Handle token refresh.

    Args:
        request (Request): Request object containing the refresh token.
        db (Session, optional): Database session for current request.

    Returns:
        dict: Access token and token type.

    """
    refresh_token = request.cookies.get("refresh_token")
    validate(
        refresh_token,
        EXC_MSG_REFRESH_TOKEN_NOT_FOUND,
        status.HTTP_401_UNAUTHORIZED,
    )

    validate(
        refresh_token not in get_invalidated_tokens(db),
        EXC_MSG_REFRESH_TOKEN_INVALID,
        status.HTTP_401_UNAUTHORIZED,
    )

    try:
        payload = jwt.decode(
            refresh_token, services.verifying_bytes, algorithms=[algorithm]
        )
        badge_number = payload.get("badge_number")
        validate(
            badge_number,
            EXC_MSG_REFRESH_TOKEN_INVALID,
            status.HTTP_401_UNAUTHORIZED,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_REFRESH_TOKEN_INVALID,
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_REFRESH_TOKEN_INVALID,
        )

    user = get_user_by_badge_number_from_db(badge_number, db)
    validate(
        user,
        EXC_MSG_REFRESH_TOKEN_INVALID,
        status.HTTP_401_UNAUTHORIZED,
    )

    new_access_token = generate_access_token(user)
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(request: Request, db: Session = Depends(get_db)):
    """Handle user logout by invalidating tokens.

    Args:
        request (Request): Request object containing the tokens.
        db (Session, optional): Database session for current request.

    Returns:
        dict: Logout success message.

    """
    access_token = request.headers.get("Authorization")
    validate(
        access_token,
        EXC_MSG_ACCESS_TOKEN_NOT_FOUND,
        status.HTTP_401_UNAUTHORIZED,
    )

    refresh_token = request.cookies.get("refresh_token")
    validate(
        refresh_token,
        EXC_MSG_REFRESH_TOKEN_NOT_FOUND,
        status.HTTP_401_UNAUTHORIZED,
    )

    invalidate_token(access_token.split(" ")[1], db)
    invalidate_token(refresh_token, db)

    return {"message": MSG_LOGOUT_SUCCESS}
