"""Module for defining report data schemas."""

from datetime import date, datetime
from typing import Union

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Schema for report generation request.

    Attributes:
        start_date (date): Start date of the report period.
        end_date (date): End date of the report period.
        employee_id (int): Optional specific employee ID to report on.
        department_id (int): Optional specific department ID to report on.
        org_unit_id (int): Optional specific org unit ID to report on.
        detail_level (str): Level of detail for PDF export
            (summary, employee_summary, detailed).

    """

    start_date: date
    end_date: date
    employee_id: Union[int, None] = None
    department_id: Union[int, None] = None
    org_unit_id: Union[int, None] = None
    detail_level: str = "summary"


class TimePeriod(BaseModel):
    """Schema for individual time clock period.

    Attributes:
        id (int): Timeclock entry ID.
        clock_in (datetime): Clock in timestamp.
        clock_out (datetime): Clock out timestamp (if available).
        hours (float): Total hours for this period.

    """

    id: int
    clock_in: datetime
    clock_out: Union[datetime, None]
    hours: float = Field(default=0.0)


class DayDetail(BaseModel):
    """Schema for daily time summary.

    Attributes:
        date (date): The date.
        total_hours (float): Total hours worked on this day.
        periods (list[TimePeriod]): Individual clock-in/out periods for the day.

    """

    date: date
    total_hours: float = Field(default=0.0)
    periods: list[TimePeriod] = Field(default_factory=list)


class MonthDetail(BaseModel):
    """Schema for monthly time summary.

    Attributes:
        month (int): Month number (1-12).
        year (int): Year.
        total_hours (float): Total hours worked in this month.
        days (list[DayDetail]): Daily breakdowns for the month.

    """

    month: int
    year: int
    total_hours: float = Field(default=0.0)
    days: list[DayDetail] = Field(default_factory=list)


class EmployeeSummary(BaseModel):
    """Schema for employee time summary within report period.

    Attributes:
        total_hours (float): Total hours worked in the period.
        regular_hours (float): Regular hours (up to standard weekly hours).
        overtime_hours (float): Overtime hours (beyond standard weekly hours).
        holiday_hours (float): Hours worked on holidays.
        days_worked (int): Number of days with clock entries.

    """

    total_hours: float = Field(default=0.0)
    regular_hours: float = Field(default=0.0)
    overtime_hours: float = Field(default=0.0)
    holiday_hours: float = Field(default=0.0)
    days_worked: int = Field(default=0)


class EmployeeReportData(BaseModel):
    """Schema for individual employee report data.

    Attributes:
        employee_id (int): Employee's unique identifier.
        badge_number (str): Employee's badge number.
        first_name (str): Employee's first name.
        last_name (str): Employee's last name.
        summary (EmployeeSummary): Summary statistics for the employee.
        months (list[MonthDetail]): Monthly breakdown of time entries.

    """

    employee_id: int
    badge_number: str
    first_name: str
    last_name: str
    summary: EmployeeSummary = Field(default_factory=EmployeeSummary)
    months: list[MonthDetail] = Field(default_factory=list)


class ReportResponse(BaseModel):
    """Schema for complete report response.

    Attributes:
        start_date (date): Report period start date.
        end_date (date): Report period end date.
        report_type (str): Type of report (employee, department, org_unit).
        filter_name (str): Name of the filter entity (department/org unit name).
        generated_at (datetime): When the report was generated.
        employees (list[EmployeeReportData]): Employee data in the report.

    """

    start_date: date
    end_date: date
    report_type: str
    filter_name: Union[str, None] = None
    generated_at: datetime = Field(default_factory=datetime.now)
    employees: list[EmployeeReportData] = Field(default_factory=list)
