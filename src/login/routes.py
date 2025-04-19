"""Module defining API for login-related operations."""

from fastapi import APIRouter, status, Depends, Request
from sqlalchemy.orm import Session
from src.database import get_db
import src.auth as auth
from src.login.constants import MSG_LOGIN_SUCCESS, MSG_LOGOUT_SUCCESS
import src.login.services as login_services
import src.login.repository as login_repository
from src.login.schemas import Login

router = APIRouter(tags=["login"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
def login(
    login_data: Login,
    req: Request,
    db: Session = Depends(get_db),
):
    """Handle user login.

    Args:
        login_data (LoginBase): The login data provided by the user.
        request (Request): The HTTP request object.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    """
    employee = login_repository.get_employee_by_id_and_password(
        login_data.id, auth.hash_value(login_data.password), db
    )
    login_services.validate_login(employee)
    req.session["auth_token"] = auth.encode_jwt_token(
        {
            "employee_id": employee.id,
            "auth_role_ids": [
                auth_role.id for auth_role in employee.auth_roles
            ],
            "permissions": login_services.generate_permission_list(employee),
        }
    )
    return {"message": MSG_LOGIN_SUCCESS}


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(
    req: Request,
):
    """Handle user logout.

    Args:
        request (Request): The HTTP request object.

    """
    req.session.clear()
    return {"message": MSG_LOGOUT_SUCCESS}
