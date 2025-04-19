"""Module for defining employee request and response schemas.

Classes:
    - EmployeeBase: Pydantic schema for request/response data.
    - EmployeeExtended: Base Pydantic schema extended with id field.

"""

from datetime import date
from typing import Optional
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from src.employee.constants import NAME_REGEX
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.auth_role.schemas import AuthRoleBase
    from src.department.schemas import DepartmentBase
    from src.org_unit.schemas import OrgUnitBase
else:
    AuthRoleBase = "AuthRoleBase"
    DepartmentBase = "DepartmentBase"
    OrgUnitBase = "OrgUnitBase"


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
    password: Optional[str] = Field(exclude=True, default=None)
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
        org_unit (list[OrgUnitBase]): The org unit the employee belongs to.
        auth_roles (list[AuthRoleBase]): List of auth roles the employee has.
        departments (list[DepartmentBase]): List of departments the employee is
            a member of.

    """

    id: int
    org_unit: OrgUnitBase
    auth_roles: list[AuthRoleBase]
    departments: list[DepartmentBase]

    model_config = ConfigDict(from_attributes=True)
