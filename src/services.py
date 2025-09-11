"""Module providing the business logic for common operations.

This module defines the service layer for handling CRUD
(Create, Read, Update, Delete) operations on common data.

"""

import os
from datetime import date, datetime, timedelta, timezone

import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session

import src.user.repository as user_repository
from src.auth_role.models import AuthRole, AuthRolePermission
from src.constants import RESOURCE_SCOPES
from src.database import SessionLocal, get_db
from src.employee.models import Employee
from src.event_log.constants import EVENT_LOG_MSGS
from src.event_log.models import EventLog
from src.org_unit.models import OrgUnit
from src.user.constants import BASE_URL as USER_URL
from src.user.constants import (
    EXC_MSG_ACCESS_TOKEN_INVALID,
    EXC_MSG_MISSING_PERMISSION,
    EXC_MSG_TOKEN_EXPIRED,
)
from src.user.models import User

rsa_private_key: rsa.RSAPrivateKey
rsa_public_key: rsa.RSAPublicKey
signing_bytes: bytes = None
verifying_bytes: bytes = None

algorithm = "RS256"
access_exp_time = 15
refresh_exp_time = 60 * 24  # 1 day
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{USER_URL}/login", scopes=RESOURCE_SCOPES
)


def validate(
    condition: bool,
    exc_msg: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> bool:
    """Return whether the provided condition is met.

    Args:
        condition (bool): The condition to validate.
        exc_msg (str): The exception message to raise.
        status_code (int): The HTTP status code to raise.

    Raises:
        HTTPException: If the provided condition is not met.

    Returns:
        bool: True if the condition is met.

    """
    if not condition:
        raise HTTPException(status_code=status_code, detail=exc_msg)
    return True


def create_root_user_if_not_exists():
    """Create a root user if it does not exist.

    This function checks if a root user exists in the database.
    If not, it creates one with all permissions.

    """
    db = SessionLocal()

    root_org_unit = db.get(OrgUnit, 0)
    if not root_org_unit:
        root_org_unit = OrgUnit(
            id=0,
            name="root",
        )
        db.add(root_org_unit)
        db.commit()

    root_employee = db.get(Employee, 0)
    if not root_employee:
        root_employee = Employee(
            id=0,
            badge_number="0",
            first_name="root",
            last_name="root",
            payroll_type="hourly",
            payroll_sync=date.today(),
            workweek_type="standard",
            time_type=True,
            allow_clocking=False,
            allow_delete=False,
            org_unit_id=root_org_unit.id,
            manager_id=None,
            holiday_group_id=None,
        )
        db.add(root_employee)
        db.commit()

    root_user = db.get(User, 0)
    if not root_user:
        root_user = User(
            id=0,
            badge_number=root_employee.badge_number,
            password=hash_password("password"),
        )
        db.add(root_user)
        db.commit()
        db.refresh(root_user)

    root_auth_role = db.get(AuthRole, 0)
    if not root_auth_role:
        root_auth_role = AuthRole(
            id=0,
            name="root",
            permissions=[
                AuthRolePermission(resource=resource)
                for resource in RESOURCE_SCOPES
            ],
        )
        db.add(root_auth_role)
        db.commit()
        db.refresh(root_auth_role)

        root_user.auth_roles.append(root_auth_role)
        db.commit()

    db.close()


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
        validate(
            condition=False,
            exc_msg=EXC_MSG_TOKEN_EXPIRED,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return payload


def generate_permission_list(user: User) -> list[str]:
    """Generate permission list for the logged-in user.

    Args:
        user (User): The user object containing user credentials.

    Returns:
        list[str]: A list of unique permissions for the user.

    """
    permissions_set = set()
    for role in user.auth_roles:
        for permission in role.permissions:
            permissions_set.add(permission.resource)
    return list(permissions_set)


def requires_permission(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    """Check if the user has the required permission.

    Args:
        jwt (str): The JWT token to check.
        resource (str): The resource to check.
        db (Session): The database session.

    Returns:
        int: The user id if the permission is granted.

    """
    validate(
        token not in user_repository.get_invalidated_tokens(db),
        EXC_MSG_ACCESS_TOKEN_INVALID,
        status.HTTP_401_UNAUTHORIZED,
    )
    payload = decode_jwt_token(token)
    token_scopes = payload.get("scopes", [])
    for scope in security_scopes.scopes:
        validate(
            scope in token_scopes,
            EXC_MSG_MISSING_PERMISSION,
            status.HTTP_403_FORBIDDEN,
        )
    return payload.get("sub")


def create_event_log(
    event_entity: str,
    event_type: str,
    format_args: dict,
    badge_number: str,
    db: Session = Depends(get_db),
) -> None:
    """Create an event log entry.

    Args:
        event_entity (str): Entity associated with the event.
        event_type (str): Event type (e.g., CREATE, UPDATE, DELETE).
        format_args (dict): Arguments to format the event log message.
        user_id (int): User ID associated with the event.
        db (Session): The database session.

    """
    event_log_msg = EVENT_LOG_MSGS[event_entity][event_type]
    event_log_msg = event_log_msg.format(**format_args)
    event_log = EventLog(
        log=event_log_msg,
        timestamp=datetime.now(timezone.utc),
        badge_number=badge_number,
    )
    db.add(event_log)
    db.commit()


def generate_dummy_data():
    """Generate dummy data for development environment.
    
    This function creates sample data for all entities in the system
    to help with development and testing.
    """
    from src.config import Settings
    
    settings = Settings()
    if settings.ENVIRONMENT.lower() != "development":
        return  # Only generate dummy data in development environment
    
    db = SessionLocal()
    
    try:
        # Import all models
        from src.org_unit.models import OrgUnit
        from src.employee.models import Employee
        from src.user.models import User
        from src.auth_role.models import AuthRole, AuthRolePermission, AuthRoleMembership
        from src.department.models import Department, DepartmentMembership
        from src.holiday_group.models import HolidayGroup, Holiday
        from src.timeclock.models import Timeclock
        from src.event_log.models import EventLog
        
        print("Generating dummy data for development environment...")
        
        # Create additional org units
        org_units_data = [
            {"id": 1, "name": "Engineering"},
            {"id": 2, "name": "Sales"},
            {"id": 3, "name": "Marketing"},
            {"id": 4, "name": "HR"},
        ]
        
        for org_data in org_units_data:
            if not db.get(OrgUnit, org_data["id"]):
                org_unit = OrgUnit(**org_data)
                db.add(org_unit)
        
        # Create departments
        departments_data = [
            {"id": 1, "name": "Backend Development"},
            {"id": 2, "name": "Frontend Development"},
            {"id": 3, "name": "Sales Team"},
            {"id": 4, "name": "Marketing Team"},
        ]
        
        for dept_data in departments_data:
            if not db.get(Department, dept_data["id"]):
                department = Department(**dept_data)
                db.add(department)
        
        # Create holiday groups
        holiday_groups_data = [
            {"id": 1, "name": "US Holidays"},
            {"id": 2, "name": "Company Holidays"},
        ]
        
        for hg_data in holiday_groups_data:
            if not db.get(HolidayGroup, hg_data["id"]):
                holiday_group = HolidayGroup(**hg_data)
                db.add(holiday_group)
        
        # Commit the basic entities first
        db.commit()
        
        # Create holidays
        holidays_data = [
            {"name": "New Year's Day", "start_date": date(2024, 1, 1), "end_date": date(2024, 1, 1), "holiday_group_id": 1},
            {"name": "Independence Day", "start_date": date(2024, 7, 4), "end_date": date(2024, 7, 4), "holiday_group_id": 1},
            {"name": "Christmas", "start_date": date(2024, 12, 25), "end_date": date(2024, 12, 25), "holiday_group_id": 1},
            {"name": "Company Retreat", "start_date": date(2024, 6, 15), "end_date": date(2024, 6, 16), "holiday_group_id": 2},
        ]
        
        for holiday_data in holidays_data:
            existing_holiday = db.query(Holiday).filter_by(
                name=holiday_data["name"], 
                holiday_group_id=holiday_data["holiday_group_id"]
            ).first()
            if not existing_holiday:
                holiday = Holiday(**holiday_data)
                db.add(holiday)
        
        # Create employees
        employees_data = [
            {"id": 1, "badge_number": "EMP001", "first_name": "John", "last_name": "Doe", "payroll_type": "salary", "payroll_sync": date.today(), "workweek_type": "standard", "time_type": True, "allow_clocking": True, "allow_delete": True, "org_unit_id": 1, "manager_id": None, "holiday_group_id": 1},
            {"id": 2, "badge_number": "EMP002", "first_name": "Jane", "last_name": "Smith", "payroll_type": "hourly", "payroll_sync": date.today(), "workweek_type": "standard", "time_type": True, "allow_clocking": True, "allow_delete": True, "org_unit_id": 1, "manager_id": 1, "holiday_group_id": 1},
            {"id": 3, "badge_number": "EMP003", "first_name": "Bob", "last_name": "Johnson", "payroll_type": "hourly", "payroll_sync": date.today(), "workweek_type": "standard", "time_type": True, "allow_clocking": True, "allow_delete": True, "org_unit_id": 2, "manager_id": 1, "holiday_group_id": 1},
            {"id": 4, "badge_number": "EMP004", "first_name": "Alice", "last_name": "Brown", "payroll_type": "salary", "payroll_sync": date.today(), "workweek_type": "standard", "time_type": True, "allow_clocking": True, "allow_delete": True, "org_unit_id": 3, "manager_id": None, "holiday_group_id": 2},
        ]
        
        for emp_data in employees_data:
            if not db.get(Employee, emp_data["id"]):
                employee = Employee(**emp_data)
                db.add(employee)
        
        # Create users
        users_data = [
            {"id": 1, "badge_number": "EMP001", "password": hash_password("password123")},
            {"id": 2, "badge_number": "EMP002", "password": hash_password("password123")},
            {"id": 3, "badge_number": "EMP003", "password": hash_password("password123")},
            {"id": 4, "badge_number": "EMP004", "password": hash_password("password123")},
        ]
        
        for user_data in users_data:
            if not db.get(User, user_data["id"]):
                user = User(**user_data)
                db.add(user)
        
        # Create auth roles
        auth_roles_data = [
            {"id": 1, "name": "Employee"},
            {"id": 2, "name": "Manager"},
            {"id": 3, "name": "Administrator"},
        ]
        
        for role_data in auth_roles_data:
            if not db.get(AuthRole, role_data["id"]):
                auth_role = AuthRole(**role_data)
                # Add some basic permissions
                if role_data["name"] == "Employee":
                    auth_role.permissions = [
                        AuthRolePermission(resource="employee.read"),
                        AuthRolePermission(resource="timeclock.create"),
                        AuthRolePermission(resource="timeclock.read"),
                    ]
                elif role_data["name"] == "Manager":
                    auth_role.permissions = [
                        AuthRolePermission(resource="employee.read"),
                        AuthRolePermission(resource="employee.update"),
                        AuthRolePermission(resource="timeclock.read"),
                        AuthRolePermission(resource="department.read"),
                    ]
                else:  # Administrator
                    auth_role.permissions = [
                        AuthRolePermission(resource=resource)
                        for resource in ["employee.create", "employee.read", "employee.update", "employee.delete",
                                       "department.create", "department.read", "department.update", "department.delete",
                                       "auth_role.create", "auth_role.read", "auth_role.update", "auth_role.delete"]
                    ]
                db.add(auth_role)
        
        # Commit before creating relationships
        db.commit()
        
        # Create auth role memberships
        role_memberships = [
            {"auth_role_id": 1, "user_id": 2},  # Jane is Employee
            {"auth_role_id": 1, "user_id": 3},  # Bob is Employee  
            {"auth_role_id": 2, "user_id": 1},  # John is Manager
            {"auth_role_id": 3, "user_id": 4},  # Alice is Administrator
        ]
        
        for membership in role_memberships:
            existing = db.query(AuthRoleMembership).filter_by(
                auth_role_id=membership["auth_role_id"],
                user_id=membership["user_id"]
            ).first()
            if not existing:
                auth_membership = AuthRoleMembership(**membership)
                db.add(auth_membership)
        
        # Create department memberships
        dept_memberships = [
            {"department_id": 1, "employee_id": 1},  # John in Backend
            {"department_id": 1, "employee_id": 2},  # Jane in Backend
            {"department_id": 2, "employee_id": 3},  # Bob in Frontend
            {"department_id": 4, "employee_id": 4},  # Alice in Marketing
        ]
        
        for membership in dept_memberships:
            existing = db.query(DepartmentMembership).filter_by(
                department_id=membership["department_id"],
                employee_id=membership["employee_id"]
            ).first()
            if not existing:
                dept_membership = DepartmentMembership(**membership)
                db.add(dept_membership)
        
        # Create some sample timeclock entries
        timeclock_entries = [
            {"badge_number": "EMP001", "timestamp": datetime.now(timezone.utc) - timedelta(hours=8)},
            {"badge_number": "EMP002", "timestamp": datetime.now(timezone.utc) - timedelta(hours=7)},
            {"badge_number": "EMP003", "timestamp": datetime.now(timezone.utc) - timedelta(hours=6)},
        ]
        
        for entry in timeclock_entries:
            timeclock = Timeclock(**entry)
            db.add(timeclock)
        
        # Create some sample event logs
        event_logs = [
            {"log": "Employee EMP001 clocked in", "timestamp": datetime.now(timezone.utc) - timedelta(hours=8), "badge_number": "EMP001"},
            {"log": "Employee EMP002 clocked in", "timestamp": datetime.now(timezone.utc) - timedelta(hours=7), "badge_number": "EMP002"},
            {"log": "Employee EMP003 clocked in", "timestamp": datetime.now(timezone.utc) - timedelta(hours=6), "badge_number": "EMP003"},
            {"log": "New user created", "timestamp": datetime.now(timezone.utc) - timedelta(hours=1), "badge_number": "0"},
        ]
        
        for log_data in event_logs:
            event_log = EventLog(**log_data)
            db.add(event_log)
        
        db.commit()
        print("Dummy data generation completed successfully!")
        
    except Exception as e:
        print(f"Error generating dummy data: {e}")
        db.rollback()
        raise
    finally:
        db.close()
