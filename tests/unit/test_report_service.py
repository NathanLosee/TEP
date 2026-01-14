"""Unit tests for report service business logic."""

from datetime import date, datetime, time, timedelta
from unittest.mock import Mock, MagicMock

import pytest

from src.report.constants import STANDARD_HOURS_PER_WEEK
from src.report.schemas import EmployeeSummary
from src.report.service import (
    _calculate_employee_summary,
    _calculate_period_hours,
    _get_holidays_for_employee,
    _organize_entries_by_month,
)
from src.timeclock.models import TimeclockEntry


def create_mock_entry(
    id: int,
    badge_number: str,
    clock_in: datetime,
    clock_out: datetime | None = None,
) -> TimeclockEntry:
    """Create a mock timeclock entry for testing."""
    entry = Mock(spec=TimeclockEntry)
    entry.id = id
    entry.badge_number = badge_number
    entry.clock_in = clock_in
    entry.clock_out = clock_out
    return entry


def create_mock_holiday(start_date: date, end_date: date):
    """Create a mock holiday for testing."""
    holiday = Mock()
    holiday.start_date = start_date
    holiday.end_date = end_date
    return holiday


class TestCalculatePeriodHours:
    """Tests for _calculate_period_hours function."""

    def test_calculate_period_hours_complete_entry(self):
        """Test calculating hours for a completed entry."""
        clock_in = datetime(2024, 1, 1, 9, 0, 0)
        clock_out = datetime(2024, 1, 1, 17, 0, 0)  # 8 hours
        entry = create_mock_entry(1, "123", clock_in, clock_out)

        hours = _calculate_period_hours(entry)

        assert hours == 8.0

    def test_calculate_period_hours_partial_hour(self):
        """Test calculating hours with partial hours (30 minutes)."""
        clock_in = datetime(2024, 1, 1, 9, 0, 0)
        clock_out = datetime(2024, 1, 1, 9, 30, 0)  # 0.5 hours
        entry = create_mock_entry(1, "123", clock_in, clock_out)

        hours = _calculate_period_hours(entry)

        assert hours == 0.5

    def test_calculate_period_hours_incomplete_entry(self):
        """Test calculating hours for entry without clock_out."""
        clock_in = datetime(2024, 1, 1, 9, 0, 0)
        entry = create_mock_entry(1, "123", clock_in, None)

        hours = _calculate_period_hours(entry)

        assert hours == 0.0

    def test_calculate_period_hours_spanning_midnight(self):
        """Test calculating hours for entry spanning midnight."""
        clock_in = datetime(2024, 1, 1, 22, 0, 0)
        clock_out = datetime(2024, 1, 2, 2, 0, 0)  # 4 hours
        entry = create_mock_entry(1, "123", clock_in, clock_out)

        hours = _calculate_period_hours(entry)

        assert hours == 4.0

    def test_calculate_period_hours_rounds_to_2_decimals(self):
        """Test that hours are rounded to 2 decimal places."""
        clock_in = datetime(2024, 1, 1, 9, 0, 0)
        clock_out = datetime(2024, 1, 1, 9, 7, 0)  # 7 minutes = 0.11666... hours
        entry = create_mock_entry(1, "123", clock_in, clock_out)

        hours = _calculate_period_hours(entry)

        assert hours == 0.12


class TestOrganizeEntriesByMonth:
    """Tests for _organize_entries_by_month function."""

    def test_organize_entries_single_day(self):
        """Test organizing entries for a single day."""
        clock_in = datetime(2024, 1, 15, 9, 0, 0)
        clock_out = datetime(2024, 1, 15, 17, 0, 0)
        entries = [create_mock_entry(1, "123", clock_in, clock_out)]

        months = _organize_entries_by_month(entries)

        assert len(months) == 1
        assert months[0].month == 1
        assert months[0].year == 2024
        assert len(months[0].days) == 1
        assert months[0].days[0].date == date(2024, 1, 15)
        assert months[0].days[0].total_hours == 8.0
        assert len(months[0].days[0].periods) == 1

    def test_organize_entries_multiple_days_same_month(self):
        """Test organizing entries across multiple days in same month."""
        entries = [
            create_mock_entry(
                1, "123",
                datetime(2024, 1, 15, 9, 0, 0),
                datetime(2024, 1, 15, 17, 0, 0)
            ),
            create_mock_entry(
                2, "123",
                datetime(2024, 1, 16, 9, 0, 0),
                datetime(2024, 1, 16, 17, 0, 0)
            ),
        ]

        months = _organize_entries_by_month(entries)

        assert len(months) == 1
        assert len(months[0].days) == 2
        assert months[0].total_hours == 16.0

    def test_organize_entries_multiple_periods_same_day(self):
        """Test organizing multiple clock periods on the same day."""
        entries = [
            create_mock_entry(
                1, "123",
                datetime(2024, 1, 15, 9, 0, 0),
                datetime(2024, 1, 15, 12, 0, 0)
            ),
            create_mock_entry(
                2, "123",
                datetime(2024, 1, 15, 13, 0, 0),
                datetime(2024, 1, 15, 17, 0, 0)
            ),
        ]

        months = _organize_entries_by_month(entries)

        assert len(months) == 1
        assert len(months[0].days) == 1
        assert len(months[0].days[0].periods) == 2
        assert months[0].days[0].total_hours == 7.0  # 3 + 4 hours

    def test_organize_entries_multiple_months(self):
        """Test organizing entries spanning multiple months."""
        entries = [
            create_mock_entry(
                1, "123",
                datetime(2024, 1, 15, 9, 0, 0),
                datetime(2024, 1, 15, 17, 0, 0)
            ),
            create_mock_entry(
                2, "123",
                datetime(2024, 2, 15, 9, 0, 0),
                datetime(2024, 2, 15, 17, 0, 0)
            ),
        ]

        months = _organize_entries_by_month(entries)

        assert len(months) == 2
        assert months[0].month == 1
        assert months[1].month == 2
        assert months[0].total_hours == 8.0
        assert months[1].total_hours == 8.0

    def test_organize_entries_empty_list(self):
        """Test organizing an empty list of entries."""
        months = _organize_entries_by_month([])

        assert len(months) == 0

    def test_organize_entries_incomplete_entry(self):
        """Test organizing entries with incomplete clock_out."""
        clock_in = datetime(2024, 1, 15, 9, 0, 0)
        entries = [create_mock_entry(1, "123", clock_in, None)]

        months = _organize_entries_by_month(entries)

        assert len(months) == 1
        assert months[0].days[0].total_hours == 0.0
        assert len(months[0].days[0].periods) == 1
        assert months[0].days[0].periods[0].hours == 0.0


class TestCalculateEmployeeSummary:
    """Tests for _calculate_employee_summary function."""

    def test_calculate_summary_no_entries(self):
        """Test calculating summary with no entries."""
        summary = _calculate_employee_summary([], [])

        assert summary.total_hours == 0.0
        assert summary.regular_hours == 0.0
        assert summary.overtime_hours == 0.0
        assert summary.holiday_hours == 0.0
        assert summary.days_worked == 0

    def test_calculate_summary_single_day_under_40(self):
        """Test calculating summary for single day under 40 hours/week."""
        entries = [
            create_mock_entry(
                1, "123",
                datetime(2024, 1, 15, 9, 0, 0),
                datetime(2024, 1, 15, 17, 0, 0)
            )
        ]

        summary = _calculate_employee_summary(entries, [])

        assert summary.total_hours == 8.0
        assert summary.regular_hours == 8.0
        assert summary.overtime_hours == 0.0
        assert summary.days_worked == 1

    def test_calculate_summary_single_week_exactly_40(self):
        """Test calculating summary for exactly 40 hours in one week."""
        monday = date(2024, 1, 15)
        entries = [
            create_mock_entry(
                i + 1, "123",
                datetime.combine(monday + timedelta(days=i), time(9, 0)),
                datetime.combine(monday + timedelta(days=i), time(17, 0))
            )
            for i in range(5)  # Mon-Fri, 8 hours each
        ]

        summary = _calculate_employee_summary(entries, [])

        assert summary.total_hours == 40.0
        assert summary.regular_hours == 40.0
        assert summary.overtime_hours == 0.0
        assert summary.days_worked == 5

    def test_calculate_summary_single_week_with_overtime(self):
        """Test calculating summary with overtime (over 40 hours/week)."""
        monday = date(2024, 1, 15)
        entries = [
            # Mon-Fri: 8 hours each = 40 hours
            *[
                create_mock_entry(
                    i + 1, "123",
                    datetime.combine(monday + timedelta(days=i), time(9, 0)),
                    datetime.combine(monday + timedelta(days=i), time(17, 0))
                )
                for i in range(5)
            ],
            # Saturday: 5 hours overtime
            create_mock_entry(
                6, "123",
                datetime.combine(monday + timedelta(days=5), time(9, 0)),
                datetime.combine(monday + timedelta(days=5), time(14, 0))
            ),
        ]

        summary = _calculate_employee_summary(entries, [])

        assert summary.total_hours == 45.0
        assert summary.regular_hours == 40.0
        assert summary.overtime_hours == 5.0
        assert summary.days_worked == 6

    def test_calculate_summary_multiple_weeks_mixed(self):
        """Test calculating summary across multiple weeks with mixed hours."""
        week1_monday = date(2024, 1, 15)
        week2_monday = week1_monday + timedelta(days=7)

        entries = [
            # Week 1: 35 hours (no overtime)
            *[
                create_mock_entry(
                    i + 1, "123",
                    datetime.combine(week1_monday + timedelta(days=i), time(9, 0)),
                    datetime.combine(week1_monday + timedelta(days=i), time(16, 0))
                )
                for i in range(5)  # 7 hours each
            ],
            # Week 2: 45 hours (5 hours overtime)
            *[
                create_mock_entry(
                    i + 6, "123",
                    datetime.combine(week2_monday + timedelta(days=i), time(9, 0)),
                    datetime.combine(week2_monday + timedelta(days=i), time(18, 0))
                )
                for i in range(5)  # 9 hours each
            ],
        ]

        summary = _calculate_employee_summary(entries, [])

        assert summary.total_hours == 80.0  # 35 + 45
        assert summary.regular_hours == 75.0  # 35 + 40
        assert summary.overtime_hours == 5.0
        assert summary.days_worked == 10

    def test_calculate_summary_with_holiday_hours(self):
        """Test calculating summary with holiday hours."""
        holiday = create_mock_holiday(date(2024, 1, 15), date(2024, 1, 15))
        entries = [
            # Regular day
            create_mock_entry(
                1, "123",
                datetime(2024, 1, 14, 9, 0, 0),
                datetime(2024, 1, 14, 17, 0, 0)
            ),
            # Holiday
            create_mock_entry(
                2, "123",
                datetime(2024, 1, 15, 9, 0, 0),
                datetime(2024, 1, 15, 17, 0, 0)
            ),
        ]

        summary = _calculate_employee_summary(entries, [holiday])

        assert summary.total_hours == 16.0
        assert summary.holiday_hours == 8.0
        assert summary.days_worked == 2

    def test_calculate_summary_multi_day_holiday(self):
        """Test calculating summary with multi-day holiday."""
        holiday = create_mock_holiday(date(2024, 1, 15), date(2024, 1, 17))
        entries = [
            create_mock_entry(
                1, "123",
                datetime(2024, 1, 15, 9, 0, 0),
                datetime(2024, 1, 15, 17, 0, 0)
            ),
            create_mock_entry(
                2, "123",
                datetime(2024, 1, 16, 9, 0, 0),
                datetime(2024, 1, 16, 17, 0, 0)
            ),
        ]

        summary = _calculate_employee_summary(entries, [holiday])

        assert summary.total_hours == 16.0
        assert summary.holiday_hours == 16.0  # Both days are holidays

    def test_calculate_summary_multiple_entries_same_day(self):
        """Test calculating summary with multiple entries on same day."""
        entries = [
            create_mock_entry(
                1, "123",
                datetime(2024, 1, 15, 9, 0, 0),
                datetime(2024, 1, 15, 12, 0, 0)
            ),
            create_mock_entry(
                2, "123",
                datetime(2024, 1, 15, 13, 0, 0),
                datetime(2024, 1, 15, 17, 0, 0)
            ),
        ]

        summary = _calculate_employee_summary(entries, [])

        assert summary.total_hours == 7.0  # 3 + 4
        assert summary.days_worked == 1  # Same day

    def test_calculate_summary_incomplete_entries(self):
        """Test calculating summary with some incomplete entries."""
        entries = [
            # Complete entry
            create_mock_entry(
                1, "123",
                datetime(2024, 1, 15, 9, 0, 0),
                datetime(2024, 1, 15, 17, 0, 0)
            ),
            # Incomplete entry (clocked in, not out)
            create_mock_entry(
                2, "123",
                datetime(2024, 1, 16, 9, 0, 0),
                None
            ),
        ]

        summary = _calculate_employee_summary(entries, [])

        assert summary.total_hours == 8.0  # Only complete entry counts
        assert summary.days_worked == 2  # Both days count

    def test_calculate_summary_week_boundary(self):
        """Test calculating summary when entries span week boundary."""
        # Sunday and Monday (different weeks)
        sunday = date(2024, 1, 14)  # Last day of week
        monday = date(2024, 1, 15)  # First day of next week

        entries = [
            # Sunday: 10 hours
            create_mock_entry(
                1, "123",
                datetime.combine(sunday, time(9, 0)),
                datetime.combine(sunday, time(19, 0))
            ),
            # Monday: 10 hours
            create_mock_entry(
                2, "123",
                datetime.combine(monday, time(9, 0)),
                datetime.combine(monday, time(19, 0))
            ),
        ]

        summary = _calculate_employee_summary(entries, [])

        # Each week evaluated separately
        assert summary.total_hours == 20.0
        assert summary.regular_hours == 20.0  # No overtime (< 40 each week)
        assert summary.overtime_hours == 0.0


class TestGetHolidaysForEmployee:
    """Tests for _get_holidays_for_employee function."""

    def test_get_holidays_no_holiday_group(self):
        """Test getting holidays when employee has no holiday group."""
        employee = Mock()
        employee.holiday_group_id = None

        db = MagicMock()

        holidays = _get_holidays_for_employee(
            employee, date(2024, 1, 1), date(2024, 1, 31), db
        )

        assert len(holidays) == 0
        db.scalars.assert_not_called()

    def test_get_holidays_with_holiday_group(self):
        """Test getting holidays when employee has holiday group."""
        employee = Mock()
        employee.holiday_group_id = 1

        mock_holiday = create_mock_holiday(date(2024, 1, 15), date(2024, 1, 15))
        db = MagicMock()
        db.scalars.return_value.all.return_value = [mock_holiday]

        holidays = _get_holidays_for_employee(
            employee, date(2024, 1, 1), date(2024, 1, 31), db
        )

        assert len(holidays) == 1
        assert holidays[0] == mock_holiday
        db.scalars.assert_called_once()
