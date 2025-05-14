"""Module defining API for login-related operations."""

from typing import Annotated
from fastapi import APIRouter, Request, Response, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.main import settings
from src.database import get_db
from src.login.constants import MSG_LOGOUT_SUCCESS
import src.login.services as login_services
import src.employee.repository as employee_repository
import src.employee.services as employee_services
from src.login.schemas import Token
from src.event_log.constants import EVENT_LOG_MSGS
import src.event_log.routes as event_log_routes
from src.event_log.schemas import EventLogBase

IDENTIFIER = "login"

router = APIRouter(tags=["login"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=Token,
)
def login(
    response: Response,
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """Handle user login.

    Args:
        login_data (LoginBase): The login data provided by the user.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    """
    employee = employee_repository.get_employee_by_id(
        int(login_data.username), db
    )
    print(employee.__dict__)
    employee_services.validate_employee_exists(employee)
    login_services.validate_login(
        login_services.verify_password(login_data.password, employee.password)
    )

    access_token = login_services.encode_jwt_token(
        {
            "sub": str(employee.id),
            "scopes": login_services.generate_permission_list(employee),
            "exp": login_services.get_expiration_time(True),
        },
    )
    refresh_token = login_services.encode_jwt_token(
        {
            "sub": str(employee.id),
            "exp": login_services.get_expiration_time(False),
        }
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
    )
    event_log_routes.create_event_log(
        EventLogBase(
            log=EVENT_LOG_MSGS[IDENTIFIER]["LOGIN"].format(
                employee_id=employee.id
            ),
            employee_id=employee.id,
        ),
        db,
    )
    return Token(access_token=access_token, token_type="bearer")


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
        request (Request): The request object containing the refresh token.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    """
    refresh_token = request.cookies.get("refresh_token")
    login_services.verify_refresh_token_exists(refresh_token)
    payload = login_services.decode_jwt_token(refresh_token)
    username = payload.get("sub")
    login_services.verify_username_exists(username)

    employee = employee_repository.get_employee_by_id(int(username), db)
    employee_services.validate_employee_exists(employee)
    new_access_token = login_services.encode_jwt_token(
        {
            "sub": str(employee.id),
            "scopes": login_services.generate_permission_list(employee),
            "exp": login_services.get_expiration_time(True),
        },
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(response: Response):
    """Handle user logout.

    Args:
        token (str): The JWT token to be invalidated.

    """
    response.delete_cookie(key="refresh_token")
    return {"message": MSG_LOGOUT_SUCCESS}
