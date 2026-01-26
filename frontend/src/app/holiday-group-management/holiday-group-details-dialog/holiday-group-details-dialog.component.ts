import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { Holiday, HolidayGroup } from '../../../services/holiday-group.service';

@Component({
  selector: 'app-holiday-group-details-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatChipsModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatDialogClose,
    MatExpansionModule,
    MatIconModule,
  ],
  templateUrl: './holiday-group-details-dialog.component.html',
  styleUrl: './holiday-group-details-dialog.component.scss',
})
export class HolidayGroupDetailsDialogComponent {
  readonly data = inject<{ holidayGroup: HolidayGroup }>(MAT_DIALOG_DATA);

  readonly weekdayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  readonly weekNumbers = ['First', 'Second', 'Third', 'Fourth', 'Last'];
  readonly monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  readonly currentYear = new Date().getFullYear();

  get holidayGroup(): HolidayGroup {
    return this.data.holidayGroup;
  }

  getStartDate(holiday: Holiday): Date {
    return holiday.start_date instanceof Date ? holiday.start_date : new Date(holiday.start_date);
  }

  getEndDate(holiday: Holiday): Date {
    return holiday.end_date instanceof Date ? holiday.end_date : new Date(holiday.end_date);
  }

  getDurationDays(holiday: Holiday): number {
    const startDate = this.getStartDate(holiday);
    const endDate = this.getEndDate(holiday);
    const diffTime = endDate.getTime() - startDate.getTime();
    return Math.ceil(diffTime / (1000 * 3600 * 24)) + 1; // +1 to include both start and end dates
  }

  getRecurrenceDescription(holiday: Holiday): string {
    if (!holiday.is_recurring) return '';

    if (holiday.recurrence_type === 'fixed') {
      const month = this.monthNames[(holiday.recurrence_month || 1) - 1];
      return `Every ${month} ${holiday.recurrence_day}`;
    } else if (holiday.recurrence_type === 'relative') {
      const week = this.weekNumbers[(holiday.recurrence_week || 1) - 1];
      const weekday = this.weekdayNames[holiday.recurrence_weekday || 0];
      const month = this.monthNames[(holiday.recurrence_month || 1) - 1];
      return `${week} ${weekday} of ${month}`;
    }

    return '';
  }

  getCurrentYearDate(holiday: Holiday): Date | null {
    if (!holiday.is_recurring) return null;

    const year = this.currentYear;

    if (holiday.recurrence_type === 'fixed') {
      return new Date(year, (holiday.recurrence_month || 1) - 1, holiday.recurrence_day || 1);
    } else if (holiday.recurrence_type === 'relative') {
      const month = (holiday.recurrence_month || 1) - 1;
      const weekday = holiday.recurrence_weekday || 0;
      const week = holiday.recurrence_week || 1;

      return this.getNthWeekdayOfMonth(year, month, weekday, week);
    }

    return null;
  }

  private getNthWeekdayOfMonth(year: number, month: number, weekday: number, n: number): Date {
    if (n === 5) { // Last occurrence
      const lastDay = new Date(year, month + 1, 0);
      let day = lastDay.getDate();

      while (day > 0) {
        const date = new Date(year, month, day);
        if (date.getDay() === (weekday + 1) % 7) { // Adjust for JS Date's weekday (0=Sunday)
          return date;
        }
        day--;
      }
    } else {
      const firstDay = new Date(year, month, 1);
      const firstWeekday = firstDay.getDay();
      const targetWeekday = (weekday + 1) % 7; // Adjust for JS Date's weekday (0=Sunday)

      let daysUntilTarget = targetWeekday - firstWeekday;
      if (daysUntilTarget < 0) daysUntilTarget += 7;

      const firstOccurrence = 1 + daysUntilTarget;
      const targetDate = firstOccurrence + (n - 1) * 7;

      return new Date(year, month, targetDate);
    }

    return new Date(year, month, 1);
  }

  /**
   * Determines if a holiday has already passed this year
   */
  isPastHoliday(holiday: Holiday): boolean {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (holiday.is_recurring) {
      const currentYearDate = this.getCurrentYearDate(holiday);
      return currentYearDate !== null && currentYearDate < today;
    } else {
      const endDate = this.getEndDate(holiday);
      return endDate < today;
    }
  }

  /**
   * Gets the effective date for sorting (recurring holidays use current year date)
   */
  getEffectiveDate(holiday: Holiday): Date {
    if (holiday.is_recurring) {
      return this.getCurrentYearDate(holiday) || new Date(this.currentYear, 0, 1);
    }
    return this.getStartDate(holiday);
  }

  /**
   * Returns holidays sorted earliest to latest
   */
  get sortedHolidays(): Holiday[] {
    return [...this.holidayGroup.holidays].sort((a, b) => {
      const dateA = this.getEffectiveDate(a);
      const dateB = this.getEffectiveDate(b);
      return dateA.getTime() - dateB.getTime();
    });
  }
}