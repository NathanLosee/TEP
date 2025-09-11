import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatTabsModule } from '@angular/material/tabs';
import {
  TimeclockEntry,
  TimeclockService,
} from '../../services/timeclock.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

interface TimeclockEntryListing {
  id?: number;
  badgeNumber: string;
  employeeName?: string;
  clockIn: Date;
  clockOut?: Date;
  totalHours?: number;
  status: string;
}

@Component({
  selector: 'app-time-entries',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatSelectModule,
    MatDialogModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatTabsModule,
  ],
  templateUrl: './timeclock-entries-management.component.html',
  styleUrl: './timeclock-entries-management.component.scss',
})
export class TimeclockEntriesManagementComponent implements OnInit {
  private timeclockService = inject(TimeclockService);
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  readonly errorDialog = inject(ErrorDialogComponent);

  timeEntries: TimeclockEntryListing[] = [];
  displayedColumns: string[] = [
    'badge_number',
    'employee_name',
    'clock_in',
    'clock_out',
    'total_hours',
    'status',
    'actions',
  ];

  filterForm: FormGroup;
  isLoading = false;

  constructor() {
    this.filterForm = this.fb.group({
      dateRange: this.fb.group({
        start: [new Date()],
        end: [new Date()],
      }),
      badge_number: [''],
      first_name: [''],
      last_name: [''],
      status: [''],
    });
  }

  ngOnInit() {
    this.setDefaultDateRange();
    this.loadTimeEntries();
    this.setupFilterForm();
  }

  setDefaultDateRange() {
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay());

    this.filterForm.patchValue({
      dateRange: {
        start: startOfWeek,
        end: today,
      },
    });
  }

  setupFilterForm() {
    this.filterForm.valueChanges.subscribe(() => {
      this.loadTimeEntries();
    });
  }

  loadTimeEntries() {
    this.isLoading = true;
    const filters = this.filterForm.value;
    this.timeclockService
      .getTimeclockEntries(
        filters.dateRange?.start,
        filters.dateRange?.end,
        filters.badge_number,
        filters.first_name,
        filters.last_name
      )
      .subscribe({
        next: (response) => {
          console.log(response);
          this.timeEntries = response.map((entry) => ({
            ...entry,
            employeeName: entry.firstName + ' ' + entry.lastName,
            totalHours: entry.clockOut
              ? this.calculateTotalHours(
                  new Date(entry.clockIn),
                  new Date(entry.clockOut)
                )
              : 0,
            status: this.getEntryStatus(entry),
          }));
          this.isLoading = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog(
            'Failed to load time entries',
            error
          );
          this.isLoading = false;
        },
      });
  }

  editEntry(entry: TimeclockEntryListing) {
    this.showSnackBar(`Edit entry for ${entry.badgeNumber}`, 'info');
  }

  deleteEntry(entry: TimeclockEntryListing) {
    this.showSnackBar(`Delete entry for ${entry.badgeNumber}`, 'info');
  }

  addManualEntry() {
    this.showSnackBar('Add manual entry feature coming soon', 'info');
  }

  calculateTotalHours(clockIn: Date, clockOut?: Date): number {
    if (!clockOut) return 0;
    return (
      Math.round(
        ((clockOut.getTime() - clockIn.getTime()) / (1000 * 60 * 60)) * 100
      ) / 100
    );
  }

  getEntryStatus(entry: TimeclockEntry): string {
    return !entry.clockOut
      ? 'clocked_in'
      : entry.clockOut.getTime() - entry.clockIn.getTime() < 4 * 60 * 60 * 1000
      ? 'incomplete'
      : 'clocked_out';
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'clocked_in':
        return 'status-active';
      case 'clocked_out':
        return 'status-complete';
      case 'incomplete':
        return 'status-warning';
      default:
        return '';
    }
  }

  getActiveEntriesCount(): number {
    return this.timeEntries.filter((e) => e.status === 'clocked_in').length;
  }

  getCompletedEntriesCount(): number {
    return this.timeEntries.filter((e) => e.status === 'clocked_out').length;
  }

  getIncompleteEntriesCount(): number {
    return this.timeEntries.filter((e) => e.status === 'incomplete').length;
  }

  private showSnackBar(
    message: string,
    type: 'success' | 'error' | 'info' = 'info'
  ) {
    this.snackBar.open(message, 'Close', {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }
}
