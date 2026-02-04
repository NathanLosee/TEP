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
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { EventLog, EventLogService } from '../../services/event-log.service';
import { PermissionService } from '../../services/permission.service';
import {
  GenericTableComponent,
  TableCellDirective,
} from '../shared/components/generic-table';
import { TableAction, TableColumn } from '../shared/models/table.models';
import { EventLogDetailDialogComponent } from './event-log-detail-dialog.component';

@Component({
  selector: 'app-event-log-management',
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
    MatTooltipModule,
    MatChipsModule,
    MatTabsModule,
    MatDialogModule,
    GenericTableComponent,
    TableCellDirective,
  ],
  templateUrl: './event-log-management.component.html',
  styleUrl: './event-log-management.component.scss',
})
export class EventLogManagementComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private eventLogService = inject(EventLogService);
  private permissionService = inject(PermissionService);
  private fb = inject(FormBuilder);
  private dialog = inject(MatDialog);

  // Data
  eventLogs: EventLog[] = [];
  filteredEventLogs: EventLog[] = [];

  // UI State
  isLoading = false;

  // Table configuration
  columns: TableColumn<EventLog>[] = [
    {
      key: 'timestamp',
      header: 'Timestamp',
      type: 'template',
    },
    {
      key: 'badge_number',
      header: 'Badge Number',
      type: 'chip',
    },
    {
      key: 'log',
      header: 'Log Message',
      type: 'template',
    },
    {
      key: 'type',
      header: 'Type',
      type: 'template',
    },
  ];

  // Table actions
  actions: TableAction<EventLog>[] = [
    {
      icon: 'visibility',
      tooltip: 'View Full Log',
      action: 'view',
    },
  ];

  // Search form
  searchForm: FormGroup;
  currentUserBadge: string | null = null;

  constructor() {
    const today = new Date();
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(today.getDate() - 7);

    this.searchForm = this.fb.group({
      startDate: [sevenDaysAgo],
      endDate: [today],
      badgeNumber: [''],
      logFilter: [''],
    });
  }

  ngOnInit() {
    this.loadCurrentUserBadge();
    this.loadEventLogs();
    this.setupSearchForm();
  }

  setupSearchForm() {
    this.searchForm.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.loadEventLogs();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadCurrentUserBadge() {
    this.permissionService.permissions$
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (permissions) => {
          this.currentUserBadge = permissions?.badge_number || null;
        },
      });
  }

  loadEventLogs() {
    const formValue = this.searchForm.value;

    if (!formValue.startDate || !formValue.endDate) {
      return;
    }

    this.isLoading = true;

    const startTimestamp = new Date(formValue.startDate).toISOString();
    const endTimestamp = new Date(formValue.endDate).toISOString();

    this.eventLogService
      .getEventLogs(
        startTimestamp,
        endTimestamp,
        formValue.badgeNumber || undefined,
        formValue.logFilter || undefined,
      )
      .subscribe({
        next: (logs) => {
          this.eventLogs = logs.sort(
            (a, b) =>
              new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
          );
          this.filteredEventLogs = this.eventLogs;
          this.isLoading = false;
        },
        error: (error) => {
          this.isLoading = false;
        },
      });
  }

  setCurrentUserFilter() {
    if (this.currentUserBadge) {
      this.searchForm.patchValue({
        badgeNumber: this.currentUserBadge,
      });
    }
  }

  hasActiveFilters(): boolean {
    const formValue = this.searchForm.value;
    return !!(formValue.badgeNumber || formValue.logFilter);
  }

  getEventType(logMessage: string): string {
    const lowerLog = logMessage.toLowerCase();
    if (lowerLog.includes('employee')) return 'employee';
    if (lowerLog.includes('timeclock') || lowerLog.includes('clock'))
      return 'timeclock';
    if (lowerLog.includes('department')) return 'department';
    if (lowerLog.includes('org unit')) return 'orgunit';
    if (lowerLog.includes('holiday')) return 'holiday';
    if (
      lowerLog.includes('user') ||
      lowerLog.includes('auth') ||
      lowerLog.includes('role')
    )
      return 'user';
    if (lowerLog.includes('report')) return 'report';
    return 'info';
  }

  getEventTypeColor(type: string): string {
    switch (type) {
      case 'employee':
        return 'primary';
      case 'timeclock':
        return 'accent';
      case 'department':
        return 'primary';
      case 'orgunit':
        return 'accent';
      case 'holiday':
        return 'primary';
      case 'user':
        return 'warn';
      case 'report':
        return 'accent';
      default:
        return '';
    }
  }

  formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }

  truncateLog(log: string, maxLength: number = 80): string {
    if (log.length <= maxLength) {
      return log;
    }
    return log.substring(0, maxLength) + '...';
  }

  onTableAction(event: { action: string; row: EventLog }) {
    if (event.action === 'view') {
      this.viewLogDetail(event.row);
    }
  }

  viewLogDetail(log: EventLog) {
    this.dialog.open(EventLogDetailDialogComponent, {
      width: '600px',
      data: log,
    });
  }
}
