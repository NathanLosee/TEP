"""Module for defining employee request and response schemas.

Classes:
    - EmployeeBase: Pydantic schema for request/response data.

"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.employee.constants import NAME_REGEX


class EmployeeBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        id (int): Employee's unique identifier.
        first_name (str): Employee's first name.
        last_name (str): Employee's last name.
        payroll_type (str): Employee's payroll type.
        payroll_sync (date): Employee's payroll sync date.
        workweek_type (str): Employee's workweek type.
        time_type (bool): Employee's time type.
            (True for full-time, False for part-time)
        allow_clocking (bool): Whether the employee is allowed to clock in/out.
        allow_delete (bool): Whether the employee is allowed to be deleted.
        org_unit_id (int): Org unit's unique identifier.
        manager_id (int): Manager's unique identifier.
        holiday_group_id (int): Holiday group's unique identifier.

    """

    id: int
    first_name: str = Field(pattern=NAME_REGEX)
    last_name: str = Field(pattern=NAME_REGEX)
    payroll_type: str
    payroll_sync: date
    workweek_type: str
    time_type: bool
    allow_clocking: bool
    allow_delete: bool
    org_unit_id: int
    manager_id: Optional[int] = Field(default=None)
    holiday_group_id: Optional[int] = Field(default=None)

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)
