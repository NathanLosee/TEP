import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
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
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableDataSource } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { TimeclockService } from '../../services/timeclock.service';
import { DisableIfNoPermissionDirective } from '../directives/has-permission.directive';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import {
  GenericTableComponent,
  TableCellDirective,
} from '../shared/components/generic-table';
import {
  TableAction,
  TableActionEvent,
  TableColumn,
} from '../shared/models/table.models';
import { TimeclockEntryFormDialogComponent } from './timeclock-entry-form-dialog/timeclock-entry-form-dialog.component';

interface TimeclockEntryListing {
  id?: number;
  badge_number: string;
  employee_name?: string;
  clock_in: Date;
  clock_out?: Date;
  total_hours?: number;
  status: string;
}

@Component({
  selector: 'app-time-entries',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatSelectModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatChipsModule,
    MatTabsModule,
    MatDialogModule,
    DisableIfNoPermissionDirective,
    GenericTableComponent,
    TableCellDirective,
  ],
  templateUrl: './timeclock-entries-management.component.html',
  styleUrl: './timeclock-entries-management.component.scss',
})
export class TimeclockEntriesManagementComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private timeclockService = inject(TimeclockService);
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);
  readonly errorDialog = inject(ErrorDialogComponent);

  dataSource = new MatTableDataSource<TimeclockEntryListing>([]);

  // Table configuration
  columns: TableColumn<TimeclockEntryListing>[] = [
    {
      key: 'badge_number',
      header: 'Badge #',
      type: 'template',
      sortable: true,
    },
    {
      key: 'employee_name',
      header: 'Employee',
      type: 'icon-text',
      icon: 'person',
      sortable: true,
    },
    {
      key: 'clock_in',
      header: 'Clock In',
      type: 'template',
      sortable: true,
    },
    {
      key: 'clock_out',
      header: 'Clock Out',
      type: 'template',
      sortable: true,
    },
    {
      key: 'total_hours',
      header: 'Total Hours',
      type: 'template',
      sortable: true,
    },
    {
      key: 'status',
      header: 'Status',
      type: 'template',
      sortable: false,
    },
  ];

  actions: TableAction<TimeclockEntryListing>[] = [
    {
      icon: 'edit',
      tooltip: 'Edit Entry',
      action: 'edit',
      permission: 'timeclock.update',
    },
    {
      icon: 'delete',
      tooltip: 'Delete Entry',
      action: 'delete',
      color: 'warn',
      permission: 'timeclock.delete',
    },
  ];

  filterForm: FormGroup;
  isLoading = false;
  userTimezone: string;

  constructor() {
    // Detect the user's timezone using Intl API
    this.userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

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
    this.filterForm.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.loadTimeEntries();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
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
        filters.last_name,
      )
      .subscribe({
        next: (response) => {
          const entries = response.map((entry: any) => ({
            id: entry.id,
            badge_number: entry.badge_number,
            employee_name: entry.first_name + ' ' + entry.last_name,
            clock_in: new Date(entry.clock_in),
            clock_out: entry.clock_out ? new Date(entry.clock_out) : undefined,
            total_hours: entry.clock_out
              ? this.calculateTotalHours(
                  new Date(entry.clock_in),
                  new Date(entry.clock_out),
                )
              : 0,
            status: this.getEntryStatus(entry),
          }));
          this.dataSource.data = entries;
          this.isLoading = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog(
            'Failed to load time entries',
            error,
          );
          this.isLoading = false;
        },
      });
  }

  editEntry(entry: TimeclockEntryListing) {
    const dialogRef = this.dialog.open(TimeclockEntryFormDialogComponent, {
      width: '600px',
      maxHeight: '90vh',
      data: {
        editEntry: {
          id: entry.id,
          badge_number: entry.badge_number,
          employee_name: entry.employee_name,
          clock_in: entry.clock_in,
          clock_out: entry.clock_out,
        },
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadTimeEntries();
        this.showSnackBar('Time entry updated successfully', 'success');
      }
    });
  }

  deleteEntry(entry: TimeclockEntryListing) {
    if (
      confirm(
        `Are you sure you want to delete the time entry for ${entry.employee_name} (${entry.badge_number})? This action cannot be undone.`,
      )
    ) {
      this.isLoading = true;
      this.timeclockService.deleteTimeclockEntry(entry.id!).subscribe({
        next: () => {
          this.loadTimeEntries();
          this.showSnackBar('Time entry deleted successfully', 'success');
        },
        error: (error) => {
          this.errorDialog.openErrorDialog(
            'Failed to delete time entry',
            error,
          );
          this.isLoading = false;
        },
      });
    }
  }

  onTableAction(event: TableActionEvent<TimeclockEntryListing>) {
    switch (event.action) {
      case 'edit':
        this.editEntry(event.row);
        break;
      case 'delete':
        this.deleteEntry(event.row);
        break;
    }
  }

  addManualEntry() {
    const dialogRef = this.dialog.open(TimeclockEntryFormDialogComponent, {
      width: '600px',
      maxHeight: '90vh',
      data: {},
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadTimeEntries();
        this.showSnackBar('Time entry created successfully', 'success');
      }
    });
  }

  calculateTotalHours(clockIn: Date, clockOut?: Date): number {
    if (!clockOut) return 0;
    return (
      Math.round(
        ((clockOut.getTime() - clockIn.getTime()) / (1000 * 60 * 60)) * 100,
      ) / 100
    );
  }

  getEntryStatus(entry: any): string {
    // API returns snake_case (clock_out) not camelCase (clockOut)
    if (!entry.clock_out) {
      return 'clocked_in';
    }

    return 'clocked_out';
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
    return this.dataSource.data.filter((e) => e.status === 'clocked_in').length;
  }

  getCompletedEntriesCount(): number {
    return this.dataSource.data.filter((e) => e.status === 'clocked_out')
      .length;
  }

  getIncompleteEntriesCount(): number {
    return this.dataSource.data.filter((e) => e.status === 'incomplete').length;
  }

  private showSnackBar(
    message: string,
    type: 'success' | 'error' | 'info' = 'info',
  ) {
    this.snackBar.open(message, 'Close', {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }
}
