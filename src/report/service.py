"""Module providing business logic for report generation."""

from datetime import date, datetime, time, timedelta
from typing import Union

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from src.department.models import Department
from src.employee.models import Employee
from src.holiday_group.models import Holiday
from src.org_unit.models import OrgUnit
from src.report.constants import (
    REPORT_TYPE_DEPARTMENT,
    REPORT_TYPE_EMPLOYEE,
    REPORT_TYPE_ORG_UNIT,
    STANDARD_HOURS_PER_WEEK,
)
from src.report.schemas import (
    DayDetail,
    EmployeeReportData,
    EmployeeSummary,
    MonthDetail,
    ReportResponse,
    TimePeriod,
)
from src.timeclock.models import TimeclockEntry


def generate_report(
    start_date: date,
    end_date: date,
    db: Session,
    employee_id: Union[int, None] = None,
    department_id: Union[int, None] = None,
    org_unit_id: Union[int, None] = None,
) -> ReportResponse:
    """Generate a timeclock report for the specified parameters.

    Args:
        start_date (date): Start date of the report period.
        end_date (date): End date of the report period.
        db (Session): Database session for the current request.
        employee_id (int): Optional employee ID to filter by.
        department_id (int): Optional department ID to filter by.
        org_unit_id (int): Optional org unit ID to filter by.

    Returns:
        ReportResponse: Complete report data.

    """
    # Determine report type and filter name
    report_type = REPORT_TYPE_EMPLOYEE
    filter_name = None

    if department_id:
        report_type = REPORT_TYPE_DEPARTMENT
        department = db.get(Department, department_id)
        filter_name = department.name if department else None
    elif org_unit_id:
        report_type = REPORT_TYPE_ORG_UNIT
        org_unit = db.get(OrgUnit, org_unit_id)
        filter_name = org_unit.name if org_unit else None

    # Get list of employees to include in report
    employees = _get_employees_for_report(
        db, employee_id, department_id, org_unit_id
    )

    # Generate report data for each employee
    employee_reports = []
    for employee in employees:
        employee_report = _generate_employee_report(
            employee, start_date, end_date, db
        )
        employee_reports.append(employee_report)

    # Create and return the report response
    return ReportResponse(
        start_date=start_date,
        end_date=end_date,
        report_type=report_type,
        filter_name=filter_name,
        generated_at=datetime.now(),
        employees=employee_reports,
    )


def _get_employees_for_report(
    db: Session,
    employee_id: Union[int, None],
    department_id: Union[int, None],
    org_unit_id: Union[int, None],
) -> list[Employee]:
    """Get list of employees to include in the report.

    Args:
        db (Session): Database session.
        employee_id (int): Optional employee ID to filter by.
        department_id (int): Optional department ID to filter by.
        org_unit_id (int): Optional org unit ID to filter by.

    Returns:
        list[Employee]: List of employees to include in report.

    """
    if employee_id:
        # Single employee report
        employee = db.get(Employee, employee_id)
        return [employee] if employee else []

    elif department_id:
        # Department report
        department = db.get(Department, department_id)
        # Filter out root employee (id=0)
        return [e for e in department.employees if e.id != 0] if department else []

    elif org_unit_id:
        # Org unit report
        org_unit = db.get(OrgUnit, org_unit_id)
        # Filter out root employee (id=0)
        return [e for e in org_unit.employees if e.id != 0] if org_unit else []

    else:
        # All employees report - filter out root employee (id=0)
        return db.scalars(select(Employee).where(Employee.id != 0)).all()


def _generate_employee_report(
    employee: Employee, start_date: date, end_date: date, db: Session
) -> EmployeeReportData:
    """Generate report data for a single employee.

    Args:
        employee (Employee): The employee to generate report for.
        start_date (date): Start date of report period.
        end_date (date): End date of report period.
        db (Session): Database session.

    Returns:
        EmployeeReportData: Report data for the employee.

    """
    # Get all timeclock entries for employee in date range
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    entries = db.scalars(
        select(TimeclockEntry)
        .where(TimeclockEntry.badge_number == employee.badge_number)
        .where(TimeclockEntry.clock_in >= start_datetime)
        .where(TimeclockEntry.clock_in <= end_datetime)
        .order_by(TimeclockEntry.clock_in)
    ).all()

    # Get holidays for this employee's holiday group
    holidays = _get_holidays_for_employee(employee, start_date, end_date, db)

    # Organize entries by month and day
    months_data = _organize_entries_by_month(entries)

    # Calculate summary statistics
    summary = _calculate_employee_summary(entries, holidays)

    return EmployeeReportData(
        employee_id=employee.id,
        badge_number=employee.badge_number,
        first_name=employee.first_name,
        last_name=employee.last_name,
        summary=summary,
        months=months_data,
    )


def _get_holidays_for_employee(
    employee: Employee, start_date: date, end_date: date, db: Session
) -> list[Holiday]:
    """Get holidays for employee's holiday group within date range.

    Args:
        employee (Employee): The employee.
        start_date (date): Start date of period.
        end_date (date): End date of period.
        db (Session): Database session.

    Returns:
        list[Holiday]: List of holidays in the period.

    """
    if not employee.holiday_group_id:
        return []

    holidays = db.scalars(
        select(Holiday)
        .where(Holiday.holiday_group_id == employee.holiday_group_id)
        .where(
            and_(
                Holiday.start_date <= end_date, Holiday.end_date >= start_date
            )
        )
    ).all()

    return holidays


def _organize_entries_by_month(
    entries: list[TimeclockEntry],
) -> list[MonthDetail]:
    """Organize timeclock entries by month and day.

    Args:
        entries (list[TimeclockEntry]): List of timeclock entries.

    Returns:
        list[MonthDetail]: Organized monthly data.

    """
    months_dict = {}

    for entry in entries:
        # Calculate hours for this entry
        hours = _calculate_period_hours(entry)

        # Create time period
        period = TimePeriod(
            id=entry.id,
            clock_in=entry.clock_in,
            clock_out=entry.clock_out,
            hours=hours,
        )

        # Get month and day keys
        entry_date = entry.clock_in.date()
        month_key = (entry_date.year, entry_date.month)

        # Initialize month if needed
        if month_key not in months_dict:
            months_dict[month_key] = MonthDetail(
                month=entry_date.month, year=entry_date.year, days=[]
            )

        # Find or create day detail
        month_detail = months_dict[month_key]
        day_detail = next(
            (d for d in month_detail.days if d.date == entry_date), None
        )

        if not day_detail:
            day_detail = DayDetail(date=entry_date)
            month_detail.days.append(day_detail)

        # Add period to day
        day_detail.periods.append(period)
        day_detail.total_hours += hours

        # Update month total
        month_detail.total_hours += hours

    # Sort months and days
    sorted_months = [
        months_dict[key] for key in sorted(months_dict.keys())
    ]
    for month in sorted_months:
        month.days.sort(key=lambda d: d.date)

    return sorted_months


def _calculate_period_hours(entry: TimeclockEntry) -> float:
    """Calculate hours for a timeclock period.

    Args:
        entry (TimeclockEntry): The timeclock entry.

    Returns:
        float: Hours worked (0 if not clocked out yet).

    """
    if not entry.clock_out:
        return 0.0

    duration = entry.clock_out - entry.clock_in
    return round(duration.total_seconds() / 3600, 2)


def _calculate_employee_summary(
    entries: list[TimeclockEntry], holidays: list[Holiday]
) -> EmployeeSummary:
    """Calculate summary statistics for employee.

    Args:
        entries (list[TimeclockEntry]): List of timeclock entries.
        holidays (list[Holiday]): List of holidays in the period.

    Returns:
        EmployeeSummary: Summary statistics.

    """
    total_hours = 0.0
    holiday_hours = 0.0
    days_worked_set = set()

    # Track hours by week for overtime calculation
    weekly_hours = {}

    for entry in entries:
        hours = _calculate_period_hours(entry)
        total_hours += hours

        # Track days worked
        entry_date = entry.clock_in.date()
        days_worked_set.add(entry_date)

        # Check if this is a holiday
        is_holiday = any(
            h.start_date <= entry_date <= h.end_date for h in holidays
        )
        if is_holiday:
            holiday_hours += hours

        # Track weekly hours (week starts on Monday)
        week_start = entry_date - timedelta(days=entry_date.weekday())
        weekly_hours[week_start] = weekly_hours.get(week_start, 0.0) + hours

    # Calculate overtime (any hours over 40 per week)
    overtime_hours = 0.0
    regular_hours = 0.0

    for week_hours in weekly_hours.values():
        if week_hours > STANDARD_HOURS_PER_WEEK:
            overtime_hours += week_hours - STANDARD_HOURS_PER_WEEK
            regular_hours += STANDARD_HOURS_PER_WEEK
        else:
            regular_hours += week_hours

    return EmployeeSummary(
        total_hours=round(total_hours, 2),
        regular_hours=round(regular_hours, 2),
        overtime_hours=round(overtime_hours, 2),
        holiday_hours=round(holiday_hours, 2),
        days_worked=len(days_worked_set),
    )
