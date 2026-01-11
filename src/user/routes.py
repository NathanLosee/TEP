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

import src.services as services
import src.user.repository as user_repository
from src.auth_role.schemas import AuthRoleExtended
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.main import settings
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
    caller_badge: str = Security(
        services.requires_permission, scopes=["user.create"]
    ),
):
    """Insert new user data.

    Args:
        request (UserBase): Request data for new user.
        db (Session, optional): Database session for current request.

    Returns:
        UserResponse: The created user.

    """
    duplicate_user = user_repository.get_user_by_badge_number(
        request.badge_number, db
    )
    services.validate(
        duplicate_user is None,
        EXC_MSG_USER_WITH_ID_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    user = user_repository.create_user(request, db)
    log_args = {"badge_number": user.badge_number}
    services.create_event_log(IDENTIFIER, "CREATE", log_args, caller_badge, db)
    return user


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        services.requires_permission, scopes=["user.read"]
    ),
):
    """Retrieve all existing users.

    Args:
        db (Session, optional): Database session for current request.

    Returns:
        list[UserResponse]: The retrieved users.

    """
    return user_repository.get_users(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        services.requires_permission, scopes=["user.read"]
    ),
):
    """Retrieve a user by a provided id.

    Args:
        id (int): User's unique identifier.
        db (Session, optional): Database session for current request.

    Returns:
        UserResponse: The user with the provided id.

    """
    user = user_repository.get_user_by_id(id, db)
    services.validate(
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
    caller_badge: str = Security(
        services.requires_permission, scopes=["user.read"]
    ),
):
    """Retrieve a user's auth roles by a provided id.

    Args:
        id (int): User's unique identifier.
        db (Session, optional): Database session for current request.

    Returns:
        list[AuthRoleExtended]: The user's auth roles.

    """
    user = user_repository.get_user_by_id(id, db)
    services.validate(
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
    caller_badge: str = Security(services.requires_permission, scopes=[]),
):
    """Update a user's password.

    Users can change their own password (requires current password).
    Users with user.update permission can change any user's password (no current password needed).

    Args:
        badge_number (str): User's badge number.
        request (UserPasswordChange): Request data for updating user.
        db (Session, optional): Database session for current request.
        caller_badge (str): Badge number of the authenticated caller.

    Returns:
        UserResponse: The updated user.

    """
    services.validate(
        request.badge_number == badge_number,
        EXC_MSG_IDS_DO_NOT_MATCH,
        status.HTTP_400_BAD_REQUEST,
    )

    user = user_repository.get_user_by_badge_number(badge_number, db)
    services.validate(
        user,
        EXC_MSG_USER_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    # Check if user is changing their own password or has admin permission
    is_self_update = caller_badge == badge_number
    caller_user = user_repository.get_user_by_badge_number(caller_badge, db)
    has_admin_permission = any(
        "user.update" in [perm.resource for perm in role.permissions]
        for role in caller_user.auth_roles
    )

    # If user is changing their own password, verify current password
    if is_self_update and not has_admin_permission:
        services.validate(
            services.verify_password(request.password, user.password),
            EXC_MSG_WRONG_PASSWORD,
            status.HTTP_403_FORBIDDEN,
        )
    # If user has admin permission, they can change without current password
    elif not has_admin_permission:
        # User doesn't have permission to change other users' passwords
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change other users' passwords",
        )

    user = user_repository.update_user(
        user,
        UserBase(badge_number=badge_number, password=request.new_password),
        db,
    )
    log_args = {
        "badge_number": user.badge_number,
        "changed_by": caller_badge,
        "is_self_update": is_self_update,
    }
    services.create_event_log(IDENTIFIER, "UPDATE_PASSWORD", log_args, caller_badge, db)
    return user


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        services.requires_permission, scopes=["user.delete"]
    ),
):
    """Delete a user by a provided id.

    Args:
        id (int): User's unique identifier.
        db (Session, optional): Database session for current request.

    """
    user = user_repository.get_user_by_id(id, db)
    services.validate(
        user,
        EXC_MSG_USER_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    user_repository.delete_user(user, db)
    log_args = {"badge_number": user.badge_number}
    services.create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)


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
    user = user_repository.get_user_by_badge_number(login.username, db)
    services.validate(
        user,
        EXC_MSG_LOGIN_FAILED,
        status.HTTP_401_UNAUTHORIZED,
    )
    services.validate(
        services.verify_password(login.password, user.password),
        EXC_MSG_LOGIN_FAILED,
        status.HTTP_401_UNAUTHORIZED,
    )

    user_repository.clean_invalidated_tokens(db)

    access_token = services.generate_access_token(user)
    refresh_token = services.generate_refresh_token(user)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
    )
    log_args = {"badge_number": user.badge_number}
    services.create_event_log(
        IDENTIFIER, "LOGIN", log_args, user.badge_number, db
    )
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
    services.validate(
        refresh_token,
        EXC_MSG_REFRESH_TOKEN_NOT_FOUND,
        status.HTTP_401_UNAUTHORIZED,
    )

    services.validate(
        refresh_token not in user_repository.get_invalidated_tokens(db),
        EXC_MSG_REFRESH_TOKEN_INVALID,
        status.HTTP_401_UNAUTHORIZED,
    )

    try:
        payload = jwt.decode(
            refresh_token, services.verifying_bytes, algorithms=[services.algorithm]
        )
        badge_number = payload.get("badge_number")
        services.validate(
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

    user = user_repository.get_user_by_badge_number(badge_number, db)
    services.validate(
        user,
        EXC_MSG_REFRESH_TOKEN_INVALID,
        status.HTTP_401_UNAUTHORIZED,
    )

    new_access_token = services.generate_access_token(user)
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
    services.validate(
        access_token,
        EXC_MSG_ACCESS_TOKEN_NOT_FOUND,
        status.HTTP_401_UNAUTHORIZED,
    )

    refresh_token = request.cookies.get("refresh_token")
    services.validate(
        refresh_token,
        EXC_MSG_REFRESH_TOKEN_NOT_FOUND,
        status.HTTP_401_UNAUTHORIZED,
    )

    user_repository.invalidate_token(access_token.split(" ")[1], db)
    user_repository.invalidate_token(refresh_token, db)

    return {"message": MSG_LOGOUT_SUCCESS}
