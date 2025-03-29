"""Module for defining employee request and response schemas.

Classes:
    - EmployeeBase: Pydantic schema for request/response data.
    - EmployeeExtended: Base Pydantic schema extended with id field.

"""

from datetime import date
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from src.auth_role.schemas import AuthRoleExtended
from src.department.schemas import DepartmentExtended
from src.employee.constants import NAME_REGEX
from src.org_unit.schemas import OrgUnitExtended


class EmployeeBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        alt_id (int): Alternate identifier of the employee's data in the
            database.
        first_name (str): First name of the employee.
        last_name (str): Last name of the employee.
        payroll_type (str): Payroll type of the employee.
        payroll_sync (date): Date of the payroll time sync for the employee.
        workweek_type (str): Workweek type of the employee.
        time_type (bool): Whether the employee is full-time or part-time.
        allow_clocking (bool): Whether the employee is allowed to clock in/out.
        allow_delete (bool): Whether the employee is allowed to be deleted.
        org_unit_id (int): Unique identifier of the org unit the employee
            belongs to.
        manager_id (int): Unique identifier of the employee's manager.

    """

    alt_id: int
    first_name: str = Field(pattern=NAME_REGEX)
    last_name: str = Field(pattern=NAME_REGEX)
    payroll_type: str
    payroll_sync: date
    workweek_type: str
    time_type: bool
    allow_clocking: bool
    allow_delete: bool
    org_unit_id: int
    manager_id: int

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)


class EmployeeExtended(EmployeeBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the employee's data in the database.

    """

    id: int
    authRoles: list[AuthRoleExtended]
    org_unit: OrgUnitExtended
    departments: list[DepartmentExtended]

    model_config = ConfigDict(from_attributes=True)


class EmployeePassword(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        id (int): Unique identifier of the employee's data in the database.
        password (str): Password of the employee.

    """

    id: int
    password: str

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)
