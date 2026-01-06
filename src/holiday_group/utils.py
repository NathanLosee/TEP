"""Utility functions for holiday generation and management."""

from calendar import monthrange
from datetime import date, timedelta


def get_nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """Get the nth occurrence of a weekday in a month.

    Args:
        year (int): Year.
        month (int): Month (1-12).
        weekday (int): Day of week (0=Monday, 6=Sunday).
        n (int): Which occurrence (1=First, 2=Second, 3=Third, 4=Fourth, 5=Last).

    Returns:
        date: The date of the nth occurrence of the weekday.

    """
    if n == 5:  # Last occurrence
        # Start from the end of the month and work backwards
        last_day = monthrange(year, month)[1]
        day = date(year, month, last_day)

        # Go backwards until we find the target weekday
        while day.weekday() != weekday:
            day -= timedelta(days=1)

        return day
    else:
        # Start from the first day of the month
        first_day = date(year, month, 1)

        # Calculate days until the first occurrence of the target weekday
        days_ahead = weekday - first_day.weekday()
        if days_ahead < 0:
            days_ahead += 7

        # Get the first occurrence
        first_occurrence = first_day + timedelta(days=days_ahead)

        # Add weeks to get to the nth occurrence
        return first_occurrence + timedelta(weeks=(n - 1))


def generate_holiday_for_year(
    holiday_name: str,
    year: int,
    recurrence_type: str,
    recurrence_month: int,
    recurrence_day: int = None,
    recurrence_week: int = None,
    recurrence_weekday: int = None,
) -> tuple[date, date]:
    """Generate holiday dates for a specific year based on recurrence pattern.

    Args:
        holiday_name (str): Name of the holiday.
        year (int): Year to generate the holiday for.
        recurrence_type (str): Type of recurrence ('fixed' or 'relative').
        recurrence_month (int): Month of the holiday (1-12).
        recurrence_day (int, optional): Day of month for fixed holidays.
        recurrence_week (int, optional): Week of month for relative holidays.
        recurrence_weekday (int, optional): Weekday for relative holidays.

    Returns:
        tuple[date, date]: Start and end dates for the holiday.

    """
    if recurrence_type == "fixed":
        # Fixed date (e.g., December 25)
        start_date = date(year, recurrence_month, recurrence_day)
        end_date = start_date
    elif recurrence_type == "relative":
        # Relative date (e.g., First Monday in September)
        start_date = get_nth_weekday_of_month(
            year, recurrence_month, recurrence_weekday, recurrence_week
        )
        end_date = start_date
    else:
        raise ValueError(f"Invalid recurrence type: {recurrence_type}")

    return start_date, end_date


def get_holidays_for_year(holidays: list, year: int) -> list[dict]:
    """Generate holiday instances for a specific year.

    Args:
        holidays: List of Holiday model instances.
        year (int): Year to generate holidays for.

    Returns:
        list[dict]: List of holiday dictionaries with name, start_date, end_date.

    """
    result = []

    for holiday in holidays:
        if holiday.is_recurring:
            # Generate the holiday for this specific year
            start_date, end_date = generate_holiday_for_year(
                holiday.name,
                year,
                holiday.recurrence_type,
                holiday.recurrence_month,
                holiday.recurrence_day,
                holiday.recurrence_week,
                holiday.recurrence_weekday,
            )
            result.append({
                "name": holiday.name,
                "start_date": start_date,
                "end_date": end_date,
            })
        else:
            # One-time holiday - only include if it falls in this year
            if holiday.start_date.year == year:
                result.append({
                    "name": holiday.name,
                    "start_date": holiday.start_date,
                    "end_date": holiday.end_date,
                })

    return result
