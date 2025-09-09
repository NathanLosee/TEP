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
    MatIconModule,
  ],
  templateUrl: './holiday-group-details-dialog.component.html',
  styleUrl: './holiday-group-details-dialog.component.scss',
})
export class HolidayGroupDetailsDialogComponent {
  readonly data = inject<{ holidayGroup: HolidayGroup }>(MAT_DIALOG_DATA);
  
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
}