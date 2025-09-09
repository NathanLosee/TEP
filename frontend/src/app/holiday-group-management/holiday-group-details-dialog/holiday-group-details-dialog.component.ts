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
import { HolidayGroup } from '../../../services/holiday-group.service';

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
}