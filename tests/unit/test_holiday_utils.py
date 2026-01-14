"""Unit tests for holiday generation utility functions."""

from datetime import date

import pytest

from src.holiday_group.utils import (
    generate_holiday_for_year,
    get_holidays_for_year,
    get_nth_weekday_of_month,
)


class TestGetNthWeekdayOfMonth:
    """Tests for get_nth_weekday_of_month function."""

    def test_first_monday_of_january_2024(self):
        """Test getting the first Monday of January 2024."""
        result = get_nth_weekday_of_month(2024, 1, 0, 1)
        # January 1, 2024 is a Monday
        assert result == date(2024, 1, 1)

    def test_second_tuesday_of_february_2024(self):
        """Test getting the second Tuesday of February 2024."""
        result = get_nth_weekday_of_month(2024, 2, 1, 2)
        # February 13, 2024 is the second Tuesday
        assert result == date(2024, 2, 13)

    def test_third_wednesday_of_march_2024(self):
        """Test getting the third Wednesday of March 2024."""
        result = get_nth_weekday_of_month(2024, 3, 2, 3)
        assert result == date(2024, 3, 20)

    def test_fourth_thursday_of_november_2024(self):
        """Test getting the fourth Thursday of November 2024 (Thanksgiving)."""
        result = get_nth_weekday_of_month(2024, 11, 3, 4)
        # Thanksgiving 2024 is November 28
        assert result == date(2024, 11, 28)

    def test_last_monday_of_may_2024(self):
        """Test getting the last Monday of May 2024 (Memorial Day)."""
        result = get_nth_weekday_of_month(2024, 5, 0, 5)
        # Memorial Day 2024 is May 27
        assert result == date(2024, 5, 27)

    def test_first_sunday_of_june_2024(self):
        """Test getting the first Sunday of June 2024."""
        result = get_nth_weekday_of_month(2024, 6, 6, 1)
        assert result == date(2024, 6, 2)

    def test_last_sunday_of_december_2024(self):
        """Test getting the last Sunday of December 2024."""
        result = get_nth_weekday_of_month(2024, 12, 6, 5)
        # Last Sunday of December 2024 is December 29
        assert result == date(2024, 12, 29)

    def test_leap_year_february(self):
        """Test handling leap year February (29 days)."""
        result = get_nth_weekday_of_month(2024, 2, 3, 5)
        # Last Thursday of February 2024 (leap year) is February 29
        assert result == date(2024, 2, 29)

    def test_non_leap_year_february(self):
        """Test handling non-leap year February (28 days)."""
        result = get_nth_weekday_of_month(2023, 2, 1, 5)
        # Last Tuesday of February 2023 (non-leap year) is February 28
        assert result == date(2023, 2, 28)

    def test_month_with_31_days(self):
        """Test handling month with 31 days (January)."""
        result = get_nth_weekday_of_month(2024, 1, 2, 5)
        # Last Wednesday of January 2024 is January 31
        assert result == date(2024, 1, 31)

    def test_month_with_30_days(self):
        """Test handling month with 30 days (April)."""
        result = get_nth_weekday_of_month(2024, 4, 1, 5)
        # Last Tuesday of April 2024 is April 30
        assert result == date(2024, 4, 30)


class TestGenerateHolidayForYear:
    """Tests for generate_holiday_for_year function."""

    def test_fixed_holiday_christmas(self):
        """Test generating Christmas (fixed date)."""
        start_date, end_date = generate_holiday_for_year(
            "Christmas",
            2024,
            "fixed",
            12,
            recurrence_day=25,
        )
        assert start_date == date(2024, 12, 25)
        assert end_date == date(2024, 12, 25)

    def test_fixed_holiday_new_years(self):
        """Test generating New Year's Day (fixed date)."""
        start_date, end_date = generate_holiday_for_year(
            "New Year's Day",
            2024,
            "fixed",
            1,
            recurrence_day=1,
        )
        assert start_date == date(2024, 1, 1)
        assert end_date == date(2024, 1, 1)

    def test_fixed_holiday_independence_day(self):
        """Test generating Independence Day (fixed date)."""
        start_date, end_date = generate_holiday_for_year(
            "Independence Day",
            2024,
            "fixed",
            7,
            recurrence_day=4,
        )
        assert start_date == date(2024, 7, 4)
        assert end_date == date(2024, 7, 4)

    def test_relative_holiday_thanksgiving(self):
        """Test generating Thanksgiving (4th Thursday of November)."""
        start_date, end_date = generate_holiday_for_year(
            "Thanksgiving",
            2024,
            "relative",
            11,
            recurrence_week=4,
            recurrence_weekday=3,
        )
        assert start_date == date(2024, 11, 28)
        assert end_date == date(2024, 11, 28)

    def test_relative_holiday_labor_day(self):
        """Test generating Labor Day (1st Monday of September)."""
        start_date, end_date = generate_holiday_for_year(
            "Labor Day",
            2024,
            "relative",
            9,
            recurrence_week=1,
            recurrence_weekday=0,
        )
        assert start_date == date(2024, 9, 2)
        assert end_date == date(2024, 9, 2)

    def test_relative_holiday_memorial_day(self):
        """Test generating Memorial Day (last Monday of May)."""
        start_date, end_date = generate_holiday_for_year(
            "Memorial Day",
            2024,
            "relative",
            5,
            recurrence_week=5,
            recurrence_weekday=0,
        )
        assert start_date == date(2024, 5, 27)
        assert end_date == date(2024, 5, 27)

    def test_invalid_recurrence_type(self):
        """Test that invalid recurrence type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid recurrence type"):
            generate_holiday_for_year(
                "Invalid Holiday",
                2024,
                "invalid_type",
                12,
            )

    def test_fixed_holiday_leap_day(self):
        """Test generating leap day (Feb 29) in leap year."""
        start_date, end_date = generate_holiday_for_year(
            "Leap Day",
            2024,
            "fixed",
            2,
            recurrence_day=29,
        )
        assert start_date == date(2024, 2, 29)
        assert end_date == date(2024, 2, 29)

    def test_fixed_holiday_month_boundary(self):
        """Test generating holiday on month boundary (1st and 31st)."""
        # First day of month
        start_date, end_date = generate_holiday_for_year(
            "First Day",
            2024,
            "fixed",
            3,
            recurrence_day=1,
        )
        assert start_date == date(2024, 3, 1)
        assert end_date == date(2024, 3, 1)

        # Last day of month (31st)
        start_date, end_date = generate_holiday_for_year(
            "Last Day",
            2024,
            "fixed",
            3,
            recurrence_day=31,
        )
        assert start_date == date(2024, 3, 31)
        assert end_date == date(2024, 3, 31)


class TestGetHolidaysForYear:
    """Tests for get_holidays_for_year function."""

    class MockHoliday:
        """Mock Holiday model for testing."""

        def __init__(
            self,
            name,
            start_date=None,
            end_date=None,
            is_recurring=False,
            recurrence_type=None,
            recurrence_month=None,
            recurrence_day=None,
            recurrence_week=None,
            recurrence_weekday=None,
        ):
            self.name = name
            self.start_date = start_date
            self.end_date = end_date
            self.is_recurring = is_recurring
            self.recurrence_type = recurrence_type
            self.recurrence_month = recurrence_month
            self.recurrence_day = recurrence_day
            self.recurrence_week = recurrence_week
            self.recurrence_weekday = recurrence_weekday

    def test_recurring_fixed_holiday(self):
        """Test generating a recurring fixed holiday."""
        holidays = [
            self.MockHoliday(
                "Christmas",
                is_recurring=True,
                recurrence_type="fixed",
                recurrence_month=12,
                recurrence_day=25,
            )
        ]

        result = get_holidays_for_year(holidays, 2024)

        assert len(result) == 1
        assert result[0]["name"] == "Christmas"
        assert result[0]["start_date"] == date(2024, 12, 25)
        assert result[0]["end_date"] == date(2024, 12, 25)

    def test_recurring_relative_holiday(self):
        """Test generating a recurring relative holiday."""
        holidays = [
            self.MockHoliday(
                "Thanksgiving",
                is_recurring=True,
                recurrence_type="relative",
                recurrence_month=11,
                recurrence_week=4,
                recurrence_weekday=3,
            )
        ]

        result = get_holidays_for_year(holidays, 2024)

        assert len(result) == 1
        assert result[0]["name"] == "Thanksgiving"
        assert result[0]["start_date"] == date(2024, 11, 28)
        assert result[0]["end_date"] == date(2024, 11, 28)

    def test_one_time_holiday_in_year(self):
        """Test including a one-time holiday that falls in the target year."""
        holidays = [
            self.MockHoliday(
                "Special Event",
                start_date=date(2024, 6, 15),
                end_date=date(2024, 6, 15),
                is_recurring=False,
            )
        ]

        result = get_holidays_for_year(holidays, 2024)

        assert len(result) == 1
        assert result[0]["name"] == "Special Event"
        assert result[0]["start_date"] == date(2024, 6, 15)
        assert result[0]["end_date"] == date(2024, 6, 15)

    def test_one_time_holiday_not_in_year(self):
        """Test excluding a one-time holiday that doesn't fall in the target year."""
        holidays = [
            self.MockHoliday(
                "Past Event",
                start_date=date(2023, 6, 15),
                end_date=date(2023, 6, 15),
                is_recurring=False,
            )
        ]

        result = get_holidays_for_year(holidays, 2024)

        assert len(result) == 0

    def test_mixed_holidays(self):
        """Test generating a mix of recurring and one-time holidays."""
        holidays = [
            self.MockHoliday(
                "Christmas",
                is_recurring=True,
                recurrence_type="fixed",
                recurrence_month=12,
                recurrence_day=25,
            ),
            self.MockHoliday(
                "Thanksgiving",
                is_recurring=True,
                recurrence_type="relative",
                recurrence_month=11,
                recurrence_week=4,
                recurrence_weekday=3,
            ),
            self.MockHoliday(
                "Company Anniversary",
                start_date=date(2024, 3, 10),
                end_date=date(2024, 3, 10),
                is_recurring=False,
            ),
            self.MockHoliday(
                "Old Event",
                start_date=date(2023, 3, 10),
                end_date=date(2023, 3, 10),
                is_recurring=False,
            ),
        ]

        result = get_holidays_for_year(holidays, 2024)

        assert len(result) == 3
        names = [h["name"] for h in result]
        assert "Christmas" in names
        assert "Thanksgiving" in names
        assert "Company Anniversary" in names
        assert "Old Event" not in names
