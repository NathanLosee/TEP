"""Module providing the business logic for common operations.

This module defines the service layer for handling CRUD
(Create, Read, Update, Delete) operations on common data.

"""

import os
import random
from datetime import date, datetime, timedelta, timezone

import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session

from src.auth_role.models import AuthRole, AuthRolePermission
from src.constants import RESOURCE_SCOPES
from src.database import SessionLocal, get_db
from src.employee.models import Employee
from src.event_log.constants import EVENT_LOG_MSGS
from src.event_log.models import EventLog
from src.org_unit.models import OrgUnit
from src.timeclock.models import TimeclockEntry
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

    In production, ROOT_PASSWORD environment variable must be set.
    In development, a secure random password is generated.

    """
    from src.main import settings

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
        # Get root password from environment
        root_password = os.getenv("ROOT_PASSWORD")

        if not root_password:
            # In production, require ROOT_PASSWORD to be set
            if settings.ENVIRONMENT.lower() == "production":
                raise RuntimeError(
                    "ROOT_PASSWORD environment variable must be set in production. "
                    "Generate a secure password and set it before starting the application."
                )

            # In development/test, generate a random secure password
            import secrets
            import string

            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            root_password = "".join(secrets.choice(alphabet) for _ in range(16))

            print("=" * 70)
            print("IMPORTANT: Root user password has been auto-generated")
            print("=" * 70)
            print(f"Username: 0")
            print(f"Password: {root_password}")
            print("=" * 70)
            print("SAVE THIS PASSWORD! You will need it to log in.")
            print("Set ROOT_PASSWORD environment variable to customize this password.")
            print("=" * 70)

        root_user = User(
            id=0,
            badge_number=root_employee.badge_number,
            password=hash_password(root_password),
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
    """Load the RSA private and public keys from local file.

    The private key is encrypted with a password from environment variable
    JWT_KEY_PASSWORD. If not set, falls back to unencrypted for development.
    """
    global rsa_private_key, rsa_public_key, signing_bytes, verifying_bytes

    # Get encryption password from environment (None if not set)
    key_password = os.getenv("JWT_KEY_PASSWORD")
    encryption_password = key_password.encode() if key_password else None

    # Determine encryption algorithm
    if encryption_password:
        encryption_algo = serialization.BestAvailableEncryption(encryption_password)
    else:
        encryption_algo = serialization.NoEncryption()
        print(
            "WARNING: JWT_KEY_PASSWORD not set. "
            "Private key will be stored unencrypted. "
            "Set JWT_KEY_PASSWORD environment variable for production."
        )

    if not os.path.exists("rsa_private_key.pem"):
        rsa_private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        with open("rsa_private_key.pem", "wb") as private_key_file:
            private_key_file.write(
                rsa_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=encryption_algo,
                )
            )
    else:
        with open("rsa_private_key.pem", "rb") as private_key_file:
            rsa_private_key = serialization.load_pem_private_key(
                private_key_file.read(), password=encryption_password
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
    plain_password_bytes = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def generate_access_token(user: User) -> str:
    """Generate an access token for the provided user.

    Args:
        user (User): The user to generate the token for.

    Returns:
        str: The generated access token.

    """
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=access_exp_time
    )
    payload = {
        "badge_number": user.badge_number,
        "exp": expiration,
        "scopes": get_scopes_from_user(user),
    }
    token = jwt.encode(payload, signing_bytes, algorithm=algorithm)
    return token


def generate_refresh_token(user: User) -> str:
    """Generate a refresh token for the provided user.

    Args:
        user (User): The user to generate the token for.

    Returns:
        str: The generated refresh token.

    """
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=refresh_exp_time
    )
    payload = {
        "badge_number": user.badge_number,
        "exp": expiration,
        "scopes": get_scopes_from_user(user),
    }
    token = jwt.encode(payload, signing_bytes, algorithm=algorithm)
    return token


def decode_jwt_token(token: str) -> dict:
    """Decode a JWT token for testing purposes.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded token payload.

    """
    payload = jwt.decode(token, verifying_bytes, algorithms=[algorithm])
    # Add 'sub' field for compatibility with tests expecting standard JWT claims
    if "badge_number" in payload and "sub" not in payload:
        payload["sub"] = payload["badge_number"]
    return payload


def encode_jwt_token(
    badge_number: str, exp: datetime, scopes: list[str] = None
) -> str:
    """Encode a JWT token for testing purposes.

    Args:
        badge_number (str): The badge number to include in the token.
        exp (datetime): The expiration time for the token.
        scopes (list[str]): The scopes to include in the token.

    Returns:
        str: The encoded JWT token.

    """
    if scopes is None:
        scopes = []
    payload = {"badge_number": badge_number, "exp": exp, "scopes": scopes}
    token = jwt.encode(payload, signing_bytes, algorithm=algorithm)
    return token


def get_scopes_from_user(user: User) -> list[str]:
    """Get the scopes for the provided user.

    Args:
        user (User): The user to get the scopes for.

    Returns:
        list[str]: The scopes for the user.

    """
    scopes = set()
    for role in user.auth_roles:
        for permission in role.permissions:
            scopes.add(permission.resource)

    return list(scopes)


def requires_permission(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    """Verify that the provided token has the required scopes.

    Args:
        security_scopes (SecurityScopes): The required scopes.
        token (str): The token to verify.
        db (Session): Database session for the current request.

    Raises:
        HTTPException: If the token is invalid or missing required scopes.

    Returns:
        str: The badge number of the user.

    """
    try:
        payload = jwt.decode(token, verifying_bytes, algorithms=[algorithm])
        badge_number: str = payload.get("badge_number")
        if badge_number is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=EXC_MSG_ACCESS_TOKEN_INVALID,
            )

        user_scopes = payload.get("scopes", [])

        for scope in security_scopes.scopes:
            if scope not in user_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=EXC_MSG_MISSING_PERMISSION,
                )

        return badge_number

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_TOKEN_EXPIRED,
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_ACCESS_TOKEN_INVALID,
        )


def create_event_log(
    identifier: str,
    action: str,
    log_args: dict,
    caller_badge: str,
    db: Session,
):
    """Create an event log entry.

    Args:
        identifier (str): The identifier for the event.
        action (str): The action performed.
        log_args (dict): Arguments to format the log message.
        caller_badge (str): The badge number of the user.
        db (Session): Database session for the current request.

    """
    message_template = EVENT_LOG_MSGS[identifier][action]
    message = message_template.format(**log_args)

    event_log = EventLog(
        badge_number=caller_badge,
        log=message,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(event_log)
    db.commit()


def get_license_status(db: Session) -> dict:
    """Check current license status.

    Args:
        db (Session): Database session for the current request.

    Returns:
        dict: License status with keys:
            - is_active (bool): Whether a license is currently active
            - license_key (str | None): The active license key if one exists
            - activated_at (datetime | None): When the license was activated
            - server_id (str | None): Machine identifier if bound

    """
    import src.license.repository as license_repository

    license_obj = license_repository.get_active_license(db)

    if license_obj:
        return {
            "is_active": True,
            "license_key": license_obj.license_key,
            "activated_at": license_obj.activated_at,
            "server_id": license_obj.server_id,
        }
    else:
        return {
            "is_active": False,
            "license_key": None,
            "activated_at": None,
            "server_id": None,
        }


def requires_license(db: Session = Depends(get_db)) -> None:
    """Dependency function to check if a valid license exists.

    Raises HTTPException (403) if no active license is found.
    This should be used as a dependency for admin endpoints.

    Args:
        db (Session): Database session for the current request.

    Raises:
        HTTPException: 403 Forbidden if no valid license exists.

    """
    from src.license.constants import EXC_MSG_LICENSE_REQUIRED

    license_status = get_license_status(db)

    if not license_status["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=EXC_MSG_LICENSE_REQUIRED,
        )


def clear_database():
    # Import all models needed for cleanup
    from src.auth_role.models import AuthRole, AuthRolePermission
    from src.department.models import Department, DepartmentMembership
    from src.employee.models import Employee
    from src.event_log.models import EventLog
    from src.holiday_group.models import Holiday, HolidayGroup
    from src.org_unit.models import OrgUnit
    from src.registered_browser.models import RegisteredBrowser
    from src.timeclock.models import TimeclockEntry
    from src.user.models import User

    # Delete all existing data from tables
    print("Clearing all existing data...")
    db = SessionLocal()

    try:
        # Delete in reverse order of dependencies to avoid foreign key constraints
        # NOTE: Preserve root records (id=0) for OrgUnit, Employee, User, and AuthRole

        # Level 1: Most dependent tables (no other tables depend on these)
        db.query(TimeclockEntry).delete()  # depends on Employee
        db.query(RegisteredBrowser).delete()  # depends on Employee
        db.query(EventLog).delete()  # depends on Employee (badge_number)
        db.query(
            DepartmentMembership
        ).delete()  # depends on Employee & Department

        # Level 2: User and AuthRole relationships (exclude root user id=0)
        db.query(AuthRolePermission).filter(
            AuthRolePermission.auth_role_id != 0
        ).delete()
        # Clear User-AuthRole many-to-many relationships (except root)
        for user in db.query(User).filter(User.id != 0).all():
            user.auth_roles.clear()
        db.commit()

        db.query(User).filter(User.id != 0).delete()  # preserve root user
        db.query(AuthRole).filter(
            AuthRole.id != 0
        ).delete()  # preserve root role

        # Level 3: Employee (exclude root employee id=0)
        # Clear manager relationships first (self-reference)
        db.query(Employee).filter(Employee.id != 0).update(
            {Employee.manager_id: None}
        )
        db.commit()
        db.query(Employee).filter(Employee.id != 0).delete()

        # Level 4: Tables that Employee depended on
        db.query(Holiday).delete()  # depends on HolidayGroup
        db.query(
            HolidayGroup
        ).delete()  # was referenced by Employee (now deleted)
        db.query(Department).delete()  # was referenced by DepartmentMembership
        db.query(OrgUnit).filter(
            OrgUnit.id != 0
        ).delete()  # preserve root org_unit

        db.commit()
        print(
            "All existing data cleared successfully (root records preserved)."
        )
    except Exception as e:
        print(f"Warning: Error clearing data: {e}")
        db.rollback()
        # Continue anyway - might be first run with empty tables

    db.close()


def generate_dummy_data():
    """Generate comprehensive dummy data for development environment.

    This function creates sample data for all entities in the system
    using API route functions to ensure proper event log generation.
    """

    print("\n" + "=" * 60)
    print("Generating comprehensive dummy data for development...")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Import route functions (these call event logging automatically)
        from src.auth_role import routes as auth_role_routes
        from src.auth_role.schemas import AuthRoleBase, PermissionBase
        from src.department import routes as department_routes
        from src.department.schemas import DepartmentBase
        from src.employee import routes as employee_routes
        from src.employee.schemas import EmployeeBase
        from src.holiday_group import routes as holiday_group_routes
        from src.holiday_group.schemas import HolidayBase, HolidayGroupBase
        from src.org_unit import routes as org_unit_routes
        from src.org_unit.schemas import OrgUnitBase
        from src.registered_browser import repository as browser_repository
        from src.registered_browser.schemas import RegisteredBrowserCreate
        from src.timeclock import routes as timeclock_routes
        from src.user import routes as user_routes
        from src.user.schemas import UserBase

        print("\n[1/7] Creating organizational units...")
        org_units_data = [
            "Engineering",
            "Sales",
            "Marketing",
            "Operations",
            "Customer Support",
        ]
        org_units = {}
        for name in org_units_data:
            org = org_unit_routes.create_org_unit(
                OrgUnitBase(name=name), db, "0"
            )
            org_units[name] = org
            print(f"  [OK] Created: {name}")

        print("\n[2/7] Creating departments...")
        departments_data = [
            "Backend Development",
            "Frontend Development",
            "Sales Team",
            "Marketing Team",
            "Warehouse",
            "Customer Service",
        ]
        departments = {}
        for name in departments_data:
            dept = department_routes.create_department(
                DepartmentBase(name=name), db, "0"
            )
            departments[name] = dept
            print(f"  [OK] Created: {name}")

        print("\n[3/7] Creating holiday groups with holidays...")
        hg_us = holiday_group_routes.create_holiday_group(
            HolidayGroupBase(
                name="US Holidays",
                holidays=[
                    HolidayBase(
                        name="New Year's Day",
                        start_date=datetime.fromisoformat("2024-01-01").date(),
                        end_date=datetime.fromisoformat("2024-01-01").date(),
                        is_recurring=True,
                        recurrence_type="fixed",
                        recurrence_month=1,
                        recurrence_day=1,
                    ),
                    HolidayBase(
                        name="Independence Day",
                        start_date=datetime.fromisoformat("2024-07-04").date(),
                        end_date=datetime.fromisoformat("2024-07-04").date(),
                        is_recurring=True,
                        recurrence_type="fixed",
                        recurrence_month=7,
                        recurrence_day=4,
                    ),
                    HolidayBase(
                        name="Thanksgiving",
                        start_date=datetime.fromisoformat("2024-11-28").date(),
                        end_date=datetime.fromisoformat("2024-11-28").date(),
                        is_recurring=True,
                        recurrence_type="relative",
                        recurrence_month=11,
                        recurrence_week=4,
                        recurrence_weekday=3,  # Thursday
                    ),
                    HolidayBase(
                        name="Christmas",
                        start_date=datetime.fromisoformat("2024-12-25").date(),
                        end_date=datetime.fromisoformat("2024-12-25").date(),
                        is_recurring=True,
                        recurrence_type="fixed",
                        recurrence_month=12,
                        recurrence_day=25,
                    ),
                    HolidayBase(
                        name="Labor Day",
                        start_date=datetime.fromisoformat("2024-09-02").date(),
                        end_date=datetime.fromisoformat("2024-09-02").date(),
                        is_recurring=True,
                        recurrence_type="relative",
                        recurrence_month=9,
                        recurrence_week=1,
                        recurrence_weekday=0,  # Monday
                    ),
                    HolidayBase(
                        name="Memorial Day",
                        start_date=datetime.fromisoformat("2024-05-27").date(),
                        end_date=datetime.fromisoformat("2024-05-27").date(),
                        is_recurring=True,
                        recurrence_type="relative",
                        recurrence_month=5,
                        recurrence_week=5,  # Last
                        recurrence_weekday=0,  # Monday
                    ),
                ],
            ),
            db,
            "0",
        )
        hg_intl = holiday_group_routes.create_holiday_group(
            HolidayGroupBase(
                name="International Holidays",
                holidays=[
                    HolidayBase(
                        name="Company Anniversary",
                        start_date=datetime.fromisoformat("2025-03-15").date(),
                        end_date=datetime.fromisoformat("2025-03-15").date(),
                        is_recurring=False,
                    ),
                    HolidayBase(
                        name="Summer Conference",
                        start_date=datetime.fromisoformat("2025-07-10").date(),
                        end_date=datetime.fromisoformat("2025-07-12").date(),
                        is_recurring=False,
                    ),
                    HolidayBase(
                        name="Year-End Closure",
                        start_date=datetime.fromisoformat("2025-12-26").date(),
                        end_date=datetime.fromisoformat("2025-12-31").date(),
                        is_recurring=False,
                    ),
                    HolidayBase(
                        name="Special Training Day",
                        start_date=datetime.fromisoformat("2026-02-20").date(),
                        end_date=datetime.fromisoformat("2026-02-20").date(),
                        is_recurring=False,
                    ),
                ],
            ),
            db,
            "0",
        )
        print(f"  [OK] Created: US Holidays (6 recurring holidays)")
        print(f"  [OK] Created: International Holidays (4 one-time holidays)")

        print("\n[4/7] Creating employees with hierarchy...")
        today = date.today()

        employees_data = [
            # (badge, first, last, payroll_type, org_unit, mgr, hg_id)
            ("EMP001", "John", "Doe", "salary", "Engineering", None, hg_us.id),
            (
                "EMP002",
                "Jane",
                "Smith",
                "hourly",
                "Engineering",
                "EMP001",
                hg_us.id,
            ),
            (
                "EMP003",
                "Bob",
                "Johnson",
                "hourly",
                "Engineering",
                "EMP001",
                hg_us.id,
            ),
            (
                "EMP004",
                "Alice",
                "Williams",
                "salary",
                "Engineering",
                None,
                hg_us.id,
            ),
            (
                "EMP005",
                "Charlie",
                "Brown",
                "hourly",
                "Sales",
                "EMP004",
                hg_us.id,
            ),
            (
                "EMP006",
                "Diana",
                "Davis",
                "hourly",
                "Sales",
                "EMP004",
                hg_us.id,
            ),
            ("EMP007", "Eve", "Miller", "salary", "Marketing", None, hg_us.id),
            (
                "EMP008",
                "Frank",
                "Wilson",
                "hourly",
                "Marketing",
                "EMP007",
                hg_us.id,
            ),
            (
                "EMP009",
                "Grace",
                "Moore",
                "hourly",
                "Operations",
                "EMP007",
                hg_intl.id,
            ),
            (
                "EMP010",
                "Henry",
                "Taylor",
                "hourly",
                "Operations",
                "EMP007",
                hg_intl.id,
            ),
            (
                "EMP011",
                "Ivy",
                "Anderson",
                "salary",
                "Customer Support",
                None,
                hg_us.id,
            ),
            (
                "EMP012",
                "Jack",
                "Thomas",
                "hourly",
                "Customer Support",
                "EMP011",
                hg_us.id,
            ),
        ]

        # Define which employees have external clock permissions
        # Managers and some specific employees who work remotely/flexibly
        external_clock_allowed_badges = {
            "EMP001",  # Admin - works from home sometimes
            "EMP004",  # Manager
            "EMP007",  # Manager
            "EMP011",  # Manager
            "EMP005",  # Sales - travels for work
            "EMP006",  # Sales - travels for work
        }

        employees = {}
        # First pass: create all employees without managers
        for badge, first, last, payroll, org_name, _, hg_id in employees_data:
            emp = employee_routes.create_employee(
                EmployeeBase(
                    badge_number=badge,
                    first_name=first,
                    last_name=last,
                    payroll_type=payroll,
                    payroll_sync=today,
                    workweek_type="standard",
                    time_type=True,
                    allow_clocking=True,
                    external_clock_allowed=badge in external_clock_allowed_badges,
                    allow_delete=True,
                    org_unit_id=org_units[org_name].id,
                    manager_id=None,
                    holiday_group_id=hg_id,
                ),
                db,
                "0",
            )
            employees[badge] = emp
            external_status = "external allowed" if badge in external_clock_allowed_badges else "office only"
            print(f"  [OK] Created employee: {badge} ({first} {last}) - {external_status}")

        # Second pass: update manager relationships
        for badge, _, _, _, _, manager_badge, _ in employees_data:
            if manager_badge:
                emp = employees[badge]
                manager_emp = employees[manager_badge]
                # Directly update the manager_id on the employee object
                emp.manager_id = manager_emp.id

        # Commit all manager relationship updates
        db.commit()
        print("  [OK] Updated manager relationships")

        print("\n[5/7] Creating users and auth roles...")
        role_admin = auth_role_routes.create_auth_role(
            AuthRoleBase(
                name="Admin",
                permissions=[
                    PermissionBase(resource="employee.create"),
                    PermissionBase(resource="employee.read"),
                    PermissionBase(resource="employee.update"),
                    PermissionBase(resource="employee.delete"),
                    PermissionBase(resource="department.create"),
                    PermissionBase(resource="department.read"),
                    PermissionBase(resource="department.update"),
                    PermissionBase(resource="department.delete"),
                    PermissionBase(resource="org_unit.create"),
                    PermissionBase(resource="org_unit.read"),
                    PermissionBase(resource="org_unit.update"),
                    PermissionBase(resource="org_unit.delete"),
                    PermissionBase(resource="holiday_group.create"),
                    PermissionBase(resource="holiday_group.read"),
                    PermissionBase(resource="holiday_group.update"),
                    PermissionBase(resource="holiday_group.delete"),
                    PermissionBase(resource="user.create"),
                    PermissionBase(resource="user.read"),
                    PermissionBase(resource="user.update"),
                    PermissionBase(resource="user.delete"),
                    PermissionBase(resource="auth_role.create"),
                    PermissionBase(resource="auth_role.read"),
                    PermissionBase(resource="auth_role.update"),
                    PermissionBase(resource="auth_role.delete"),
                    PermissionBase(resource="timeclock.create"),
                    PermissionBase(resource="timeclock.read"),
                    PermissionBase(resource="timeclock.update"),
                    PermissionBase(resource="timeclock.delete"),
                    PermissionBase(resource="registered_browser.create"),
                    PermissionBase(resource="registered_browser.read"),
                    PermissionBase(resource="registered_browser.delete"),
                    PermissionBase(resource="event_log.create"),
                    PermissionBase(resource="event_log.read"),
                    PermissionBase(resource="event_log.delete"),
                    PermissionBase(resource="report.read"),
                    PermissionBase(resource="report.export"),
                ],
            ),
            db,
            "0",
        )

        role_manager = auth_role_routes.create_auth_role(
            AuthRoleBase(
                name="Manager",
                permissions=[
                    PermissionBase(resource="employee.read"),
                    PermissionBase(resource="employee.update"),
                    PermissionBase(resource="timeclock.read"),
                    PermissionBase(resource="timeclock.update"),
                    PermissionBase(resource="event_log.read"),
                    PermissionBase(resource="report.read"),
                ],
            ),
            db,
            "0",
        )

        role_employee = auth_role_routes.create_auth_role(
            AuthRoleBase(
                name="Employee",
                permissions=[
                    PermissionBase(resource="employee.read"),
                    PermissionBase(resource="timeclock.create"),
                    PermissionBase(resource="timeclock.read"),
                    PermissionBase(resource="event_log.read"),
                ],
            ),
            db,
            "0",
        )
        print("  [OK] Created roles: Admin, Manager, Employee")

        # Only create user accounts for employees who need system access
        # Most employees only need to clock in/out and don't need accounts
        users_roles = [
            ("EMP001", "Admin"),    # Alice Johnson - Full admin access
            ("EMP004", "Manager"),  # David Lee - Engineering manager
            ("EMP007", "Manager"),  # Eve Miller - Marketing manager
            ("EMP011", "Manager"),  # Ivy Anderson - Customer Support manager
        ]

        for badge, role_name in users_roles:
            user = user_routes.create_user(
                UserBase(badge_number=badge, password="password123"), db, "0"
            )

            # Assign role
            role = (
                role_admin
                if role_name == "Admin"
                else (
                    role_manager if role_name == "Manager" else role_employee
                )
            )
            user.auth_roles.append(role)
            db.commit()
            print(f"  [OK] Created user: {badge} with role {role_name}")

        # Register a dummy browser for testing timeclock functionality
        print("\n  Registering company browser for testing...")
        test_browser = browser_repository.create_registered_browser(
            RegisteredBrowserCreate(
                browser_uuid="TEST-BROWSER-UUID-12345",
                browser_name="Office Kiosk - Main Entrance"
            ),
            db
        )
        print(f"  [OK] Registered browser: {test_browser.browser_name}")

        print("\n[6/7] Assigning department memberships...")
        dept_memberships = [
            ("Backend Development", ["EMP001", "EMP002", "EMP003"]),
            ("Frontend Development", ["EMP004"]),
            ("Sales Team", ["EMP005", "EMP006"]),
            ("Marketing Team", ["EMP007"]),
            ("Warehouse", ["EMP008", "EMP009", "EMP010"]),
            ("Customer Service", ["EMP011", "EMP012"]),
        ]

        for dept_name, emp_badges in dept_memberships:
            dept = departments[dept_name]
            for badge in emp_badges:
                emp = employees[badge]
                dept.employees.append(emp)
            db.commit()
            print(f"  [OK] Assigned {len(emp_badges)} employees to {dept_name}")

        print("\n[7/7] Creating timeclock entries...")
        now = datetime.now(timezone.utc)
        entry_count = 0

        # Generate entries for past 10 working days
        for day_offset in range(10, 0, -1):
            entry_date = now - timedelta(days=day_offset)

            # Skip weekends
            if entry_date.weekday() >= 5:
                continue

            for badge in employees.keys():
                # Randomize clock in/out times (8-9 AM, 4-6 PM)
                clock_in = entry_date.replace(
                    hour=8,
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0,
                )

                clock_out = entry_date.replace(
                    hour=16 + random.randint(0, 2),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0,
                )

                # Some employees might still be clocked in on most recent day
                # Use the registered browser UUID so all employees can clock in
                if day_offset == 1 and random.random() < 0.3:
                    timeclock_routes.timeclock(badge, db, x_device_uuid=test_browser.browser_uuid)
                else:
                    entry = TimeclockEntry(
                        badge_number=badge,
                        clock_in=clock_in,
                        clock_out=clock_out,
                    )
                    db.add(entry)

                entry_count += 1

        db.commit()
        print(f"  [OK] Created {entry_count} timeclock entries")

        print("\n" + "=" * 60)
        print("[SUCCESS] Comprehensive dummy data generation completed!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Org units: {len(org_units_data)}")
        print(f"  - Departments: {len(departments_data)}")
        print(f"  - Employees: {len(employees_data)}")
        print(f"  - Users: {len(users_roles)}")
        print(f"  - Timeclock entries: {entry_count}")
        print(f"  - Event logs: Auto-generated from API calls")
        print(f"\nLogin credentials: Any badge number / password123")
        print(f"   Admin user: EMP001 / password123\n")

    except Exception as e:
        print(f"\n[ERROR] Error generating dummy data: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
