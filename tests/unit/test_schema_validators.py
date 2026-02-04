"""Unit tests for Pydantic schema validators."""

from datetime import date, datetime

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from src.holiday_group.schemas import HolidayBase, HolidayGroupBase
from src.system_settings.schemas import SystemSettingsBase
from src.timeclock.schemas import TimeclockEntryBase, TimeclockEntryCreate


class TestHolidayBaseValidator:
    """Tests for HolidayBase.check_values model validator."""

    def test_start_date_after_end_date_raises(self):
        """end_date before start_date raises HTTPException 400."""
        with pytest.raises(HTTPException) as exc_info:
            HolidayBase(
                name="Test Holiday",
                start_date=date(2025, 12, 26),
                end_date=date(2025, 12, 25),
            )
        assert exc_info.value.status_code == 400

    def test_start_date_equals_end_date_passes(self):
        """start_date equal to end_date is valid."""
        holiday = HolidayBase(
            name="Test Holiday",
            start_date=date(2025, 12, 25),
            end_date=date(2025, 12, 25),
        )
        assert holiday.start_date == holiday.end_date

    def test_start_date_before_end_date_passes(self):
        """start_date before end_date is valid."""
        holiday = HolidayBase(
            name="Test Holiday",
            start_date=date(2025, 12, 24),
            end_date=date(2025, 12, 26),
        )
        assert holiday.start_date < holiday.end_date

    def test_recurring_invalid_recurrence_type_raises(self):
        """is_recurring=True with bad recurrence_type raises."""
        with pytest.raises(HTTPException) as exc_info:
            HolidayBase(
                name="Test Holiday",
                start_date=date(2025, 12, 25),
                end_date=date(2025, 12, 25),
                is_recurring=True,
                recurrence_type="weekly",
                recurrence_month=12,
            )
        assert exc_info.value.status_code == 400

    def test_recurring_none_recurrence_type_raises(self):
        """is_recurring=True with no recurrence_type raises."""
        with pytest.raises(HTTPException) as exc_info:
            HolidayBase(
                name="Test Holiday",
                start_date=date(2025, 12, 25),
                end_date=date(2025, 12, 25),
                is_recurring=True,
                recurrence_type=None,
                recurrence_month=12,
            )
        assert exc_info.value.status_code == 400

    def test_recurring_missing_recurrence_month_raises(self):
        """is_recurring=True without recurrence_month raises."""
        with pytest.raises(HTTPException) as exc_info:
            HolidayBase(
                name="Test Holiday",
                start_date=date(2025, 12, 25),
                end_date=date(2025, 12, 25),
                is_recurring=True,
                recurrence_type="fixed",
                recurrence_month=None,
            )
        assert exc_info.value.status_code == 400

    def test_recurring_fixed_missing_day_raises(self):
        """Fixed recurrence without recurrence_day raises."""
        with pytest.raises(HTTPException) as exc_info:
            HolidayBase(
                name="Test Holiday",
                start_date=date(2025, 12, 25),
                end_date=date(2025, 12, 25),
                is_recurring=True,
                recurrence_type="fixed",
                recurrence_month=12,
                recurrence_day=None,
            )
        assert exc_info.value.status_code == 400

    def test_recurring_relative_missing_week_raises(self):
        """Relative recurrence without recurrence_week raises."""
        with pytest.raises(HTTPException) as exc_info:
            HolidayBase(
                name="Test Holiday",
                start_date=date(2025, 11, 27),
                end_date=date(2025, 11, 27),
                is_recurring=True,
                recurrence_type="relative",
                recurrence_month=11,
                recurrence_week=None,
                recurrence_weekday=3,
            )
        assert exc_info.value.status_code == 400

    def test_recurring_relative_missing_weekday_raises(self):
        """Relative recurrence without recurrence_weekday raises."""
        with pytest.raises(HTTPException) as exc_info:
            HolidayBase(
                name="Test Holiday",
                start_date=date(2025, 11, 27),
                end_date=date(2025, 11, 27),
                is_recurring=True,
                recurrence_type="relative",
                recurrence_month=11,
                recurrence_week=4,
                recurrence_weekday=None,
            )
        assert exc_info.value.status_code == 400

    def test_non_recurring_without_recurrence_fields_passes(self):
        """Non-recurring holiday without recurrence fields is valid."""
        holiday = HolidayBase(
            name="Company Picnic",
            start_date=date(2025, 7, 4),
            end_date=date(2025, 7, 4),
            is_recurring=False,
        )
        assert holiday.is_recurring is False
        assert holiday.recurrence_type is None
        assert holiday.recurrence_month is None

    def test_valid_recurring_fixed_holiday_passes(self):
        """Valid recurring fixed holiday passes validation."""
        holiday = HolidayBase(
            name="Christmas Day",
            start_date=date(2025, 12, 25),
            end_date=date(2025, 12, 25),
            is_recurring=True,
            recurrence_type="fixed",
            recurrence_month=12,
            recurrence_day=25,
        )
        assert holiday.is_recurring is True
        assert holiday.recurrence_type == "fixed"
        assert holiday.recurrence_month == 12
        assert holiday.recurrence_day == 25

    def test_valid_recurring_relative_holiday_passes(self):
        """Valid recurring relative holiday passes validation."""
        holiday = HolidayBase(
            name="Thanksgiving",
            start_date=date(2025, 11, 27),
            end_date=date(2025, 11, 27),
            is_recurring=True,
            recurrence_type="relative",
            recurrence_month=11,
            recurrence_week=4,
            recurrence_weekday=3,
        )
        assert holiday.is_recurring is True
        assert holiday.recurrence_type == "relative"
        assert holiday.recurrence_week == 4
        assert holiday.recurrence_weekday == 3


class TestHolidayGroupBaseValidator:
    """Tests for HolidayGroupBase.check_values duplicate check."""

    def test_unique_holiday_names_passes(self):
        """List with unique holiday names passes validation."""
        group = HolidayGroupBase(
            name="US Holidays",
            holidays=[
                HolidayBase(
                    name="New Year",
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 1, 1),
                ),
                HolidayBase(
                    name="Independence Day",
                    start_date=date(2025, 7, 4),
                    end_date=date(2025, 7, 4),
                ),
            ],
        )
        assert len(group.holidays) == 2

    def test_duplicate_holiday_names_raises(self):
        """Duplicate holiday names in the list raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            HolidayGroupBase(
                name="US Holidays",
                holidays=[
                    HolidayBase(
                        name="Christmas",
                        start_date=date(2025, 12, 25),
                        end_date=date(2025, 12, 25),
                    ),
                    HolidayBase(
                        name="Christmas",
                        start_date=date(2025, 12, 26),
                        end_date=date(2025, 12, 26),
                    ),
                ],
            )
        assert exc_info.value.status_code == 400


class TestTimeclockEntryCreateValidator:
    """Tests for TimeclockEntryCreate.check_datetimes validator."""

    def test_clock_out_after_clock_in_passes(self):
        """clock_out >= clock_in passes validation."""
        entry = TimeclockEntryCreate(
            badge_number="EMP001",
            clock_in=datetime(2025, 1, 15, 8, 0, 0),
            clock_out=datetime(2025, 1, 15, 17, 0, 0),
        )
        assert entry.clock_out > entry.clock_in

    def test_clock_out_equals_clock_in_passes(self):
        """clock_out equal to clock_in passes validation."""
        ts = datetime(2025, 1, 15, 8, 0, 0)
        entry = TimeclockEntryCreate(
            badge_number="EMP001",
            clock_in=ts,
            clock_out=ts,
        )
        assert entry.clock_out == entry.clock_in

    def test_clock_out_before_clock_in_raises(self):
        """clock_out < clock_in raises HTTPException 400."""
        with pytest.raises(HTTPException) as exc_info:
            TimeclockEntryCreate(
                badge_number="EMP001",
                clock_in=datetime(2025, 1, 15, 17, 0, 0),
                clock_out=datetime(2025, 1, 15, 8, 0, 0),
            )
        assert exc_info.value.status_code == 400

    def test_clock_out_none_passes(self):
        """clock_out=None passes (employee still clocked in)."""
        entry = TimeclockEntryCreate(
            badge_number="EMP001",
            clock_in=datetime(2025, 1, 15, 8, 0, 0),
            clock_out=None,
        )
        assert entry.clock_out is None


class TestTimeclockEntryBaseValidator:
    """Tests for TimeclockEntryBase.check_datetimes validator."""

    def test_valid_entry_passes(self):
        """Valid TimeclockEntryBase data passes validation."""
        entry = TimeclockEntryBase(
            id=1,
            badge_number="EMP001",
            clock_in=datetime(2025, 1, 15, 8, 0, 0),
            clock_out=datetime(2025, 1, 15, 17, 0, 0),
        )
        assert entry.id == 1
        assert entry.clock_out > entry.clock_in

    def test_clock_out_before_clock_in_raises(self):
        """clock_out before clock_in raises HTTPException 400."""
        with pytest.raises(HTTPException) as exc_info:
            TimeclockEntryBase(
                id=1,
                badge_number="EMP001",
                clock_in=datetime(2025, 1, 15, 17, 0, 0),
                clock_out=datetime(2025, 1, 15, 8, 0, 0),
            )
        assert exc_info.value.status_code == 400


class TestSystemSettingsBaseValidator:
    """Tests for SystemSettingsBase.validate_colors field validator."""

    def test_valid_hex_color_uppercase_passes(self):
        """Valid uppercase hex color passes and stays uppercase."""
        settings = SystemSettingsBase(
            primary_color="#1976D2",
        )
        assert settings.primary_color == "#1976D2"

    def test_valid_hex_color_lowercase_uppercased(self):
        """Valid lowercase hex color is converted to uppercase."""
        settings = SystemSettingsBase(
            primary_color="#ff9800",
        )
        assert settings.primary_color == "#FF9800"

    def test_invalid_color_name_raises(self):
        """Non-hex color string 'red' raises ValidationError."""
        with pytest.raises(ValidationError):
            SystemSettingsBase(
                primary_color="red",
            )

    def test_invalid_short_hex_raises(self):
        """Invalid short hex '#GGG' raises ValidationError."""
        with pytest.raises(ValidationError):
            SystemSettingsBase(
                primary_color="#GGG",
            )

    def test_none_colors_pass(self):
        """None values for optional color fields pass through."""
        settings = SystemSettingsBase(
            primary_color=None,
            secondary_color=None,
            accent_color=None,
        )
        assert settings.primary_color is None
        assert settings.secondary_color is None
        assert settings.accent_color is None

    def test_company_name_within_max_length(self):
        """company_name within 255 characters is valid."""
        settings = SystemSettingsBase(
            company_name="Acme Corporation",
        )
        assert settings.company_name == "Acme Corporation"

    def test_company_name_exceeds_max_length_raises(self):
        """company_name over 255 characters raises ValidationError."""
        with pytest.raises(ValidationError):
            SystemSettingsBase(
                company_name="A" * 256,
            )

    def test_all_color_fields_validated(self):
        """All three color fields are validated and uppercased."""
        settings = SystemSettingsBase(
            primary_color="#aabbcc",
            secondary_color="#ddeeff",
            accent_color="#112233",
        )
        assert settings.primary_color == "#AABBCC"
        assert settings.secondary_color == "#DDEEFF"
        assert settings.accent_color == "#112233"
