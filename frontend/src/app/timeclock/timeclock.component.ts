import { DatePipe } from '@angular/common';
import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogActions,
  MatDialogContent,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { interval, Subscription } from 'rxjs';
import { BrowserUuidService } from '../../services/browser-uuid.service';
import { OfflineQueueService } from '../../services/offline-queue.service';
import { RegisteredBrowserService } from '../../services/registered-browser.service';
import {
  TimeclockEntry,
  TimeclockService,
} from '../../services/timeclock.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  entries: TimeclockEntry[];
}

@Component({
  selector: 'app-timeclock',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatToolbarModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule,
  ],
  templateUrl: './timeclock.component.html',
  styleUrl: './timeclock.component.scss',
})
export class TimeclockComponent implements OnInit, OnDestroy {
  private timeclockService = inject(TimeclockService);
  private browserUuidService = inject(BrowserUuidService);
  private registeredBrowserService = inject(RegisteredBrowserService);
  private offlineQueueService = inject(OfflineQueueService);
  private clockSubscription?: Subscription;
  readonly dialog = inject(MatDialog);
  readonly errorDialog = inject(ErrorDialogComponent);

  currentDateAndTime = Date.now();
  badgeNumber: string;
  isBrowserRegistered = false;
  browserName: string | null = null;
  pendingCount = 0;
  isOffline = false;

  // Recovery form state
  showRecoveryForm = false;
  recoveryCode = '';
  isRecovering = false;
  recoveryError: string | null = null;

  constructor() {
    this.badgeNumber = '';
  }

  async ngOnInit() {
    // Update the current date and time every minute
    const timer = interval(60000);
    this.clockSubscription = timer.subscribe(() => {
      this.currentDateAndTime = Date.now();
    });

    // Subscribe to offline queue state
    this.offlineQueueService.pendingCount$.subscribe(
      (count) => (this.pendingCount = count),
    );
    this.offlineQueueService.isOffline$.subscribe(
      (offline) => (this.isOffline = offline),
    );

    // Check browser registration status
    await this.checkBrowserRegistration();
  }

  async checkBrowserRegistration() {
    try {
      const fingerprint = await this.browserUuidService.generateFingerprint();
      const storedUuid = this.browserUuidService.getBrowserUuid();

      this.registeredBrowserService
        .verifyBrowser({
          fingerprint_hash: fingerprint,
          browser_uuid: storedUuid || undefined,
        })
        .subscribe({
          next: (response) => {
            this.isBrowserRegistered = response.verified;
            this.browserName = response.browser_name || null;

            // If UUID was restored from fingerprint, update localStorage
            if (response.restored && response.browser_uuid) {
              this.browserUuidService.setBrowserUuid(
                response.browser_uuid,
                response.browser_name,
              );
            }
          },
          error: (error) => {
            console.error('Browser verification failed:', error);
            this.isBrowserRegistered = false;
            this.browserName = null;
          },
        });
    } catch (error) {
      console.error('Failed to generate fingerprint:', error);
      this.isBrowserRegistered = false;
      this.browserName = null;
    }
  }

  ngOnDestroy() {
    // Unsubscribe from the timer to prevent memory leaks
    if (this.clockSubscription) {
      this.clockSubscription.unsubscribe();
    }
  }

  /**
   * Clock in/out for the employee ID, with offline fallback
   */
  clockInOut() {
    if (this.isOffline) {
      this.queueOfflinePunch();
      return;
    }

    this.timeclockService.timeclock(this.badgeNumber).subscribe({
      next: (response) => {
        this.openTimeclockDialog(this.badgeNumber, response.message);
        this.badgeNumber = '';
      },
      error: (error) => {
        if (this.isNetworkError(error)) {
          this.queueOfflinePunch();
        } else {
          this.errorDialog.openErrorDialog('Failed to clock in/out', error);
        }
      },
    });
  }

  private queueOfflinePunch() {
    this.offlineQueueService.enqueue(this.badgeNumber).then(() => {
      this.openTimeclockDialog(
        this.badgeNumber,
        'Punch queued (offline)',
      );
      this.badgeNumber = '';
    });
  }

  private isNetworkError(error: unknown): boolean {
    if (error && typeof error === 'object' && 'status' in error) {
      const status = (error as { status: number }).status;
      return status === 0 || status === undefined;
    }
    return error instanceof TypeError;
  }

  /**
   * Check the status of the employee ID
   */
  checkStatus() {
    this.timeclockService.checkStatus(this.badgeNumber).subscribe({
      next: (response) => {
        console.log(response);
        this.openTimeclockDialog(this.badgeNumber, response.message);
      },
      error: (error) => {
        this.errorDialog.openErrorDialog('Failed to check status', error);
      },
    });
  }

  /**
   * View timeclock history for the employee
   */
  viewHistory() {
    this.openHistoryDialog(this.badgeNumber);
  }

  /**
   * Recover browser registration using browser ID
   */
  async recoverBrowser() {
    if (!this.recoveryCode || this.isRecovering) {
      return;
    }

    // Clear any previous errors
    this.recoveryError = null;
    this.isRecovering = true;

    try {
      // Format the browser ID (uppercase, trim whitespace)
      const formattedCode = this.recoveryCode.toUpperCase().trim();

      // Check if this UUID conflicts with current session
      if (this.browserUuidService.isUuidInActiveSession(formattedCode)) {
        this.recoveryError =
          'This browser ID is already in use in another browser session on this device.';
        this.isRecovering = false;
        return;
      }

      // Generate fingerprint for recovery
      const fingerprint = await this.browserUuidService.generateFingerprint();

      // Call recovery endpoint
      this.registeredBrowserService
        .recoverBrowser({
          recovery_code: formattedCode,
          fingerprint_hash: fingerprint,
        })
        .subscribe({
          next: (response) => {
            // Save recovered UUID to localStorage and sessionStorage
            this.browserUuidService.setBrowserUuid(
              response.browser_uuid,
              response.browser_name,
            );

            // Update UI state
            this.isBrowserRegistered = true;
            this.browserName = response.browser_name;
            this.showRecoveryForm = false;
            this.recoveryCode = '';
            this.isRecovering = false;
            this.recoveryError = null;

            // Show success message
            alert(
              `Browser registration recovered successfully!\nBrowser: ${response.browser_name}`,
            );
          },
          error: (error) => {
            console.error('Recovery failed:', error);
            this.isRecovering = false;

            // Display user-friendly error message
            if (error.status === 404) {
              this.recoveryError =
                'Browser ID not found or browser is inactive.';
            } else if (error.status === 400) {
              this.recoveryError =
                'Invalid browser ID format. Expected: WORD-WORD-WORD-NUMBER';
            } else {
              this.recoveryError =
                'Recovery failed. Please check your browser ID and try again.';
            }
          },
        });
    } catch (error) {
      console.error('Failed to generate fingerprint:', error);
      this.recoveryError = 'Failed to initialize recovery. Please try again.';
      this.isRecovering = false;
    }
  }

  /**
   * Cancel recovery and hide the form
   */
  cancelRecovery() {
    this.showRecoveryForm = false;
    this.recoveryCode = '';
    this.recoveryError = null;
    this.isRecovering = false;
  }

  /**
   * Open the dialog to display the timeclock status
   * @param timeclockStatus The timeclock status of the employee
   */
  openTimeclockDialog(badgeNumber: string, timeclockStatus: string): void {
    const dialogRef = this.dialog.open(TimeclockDialog, {
      height: '300px',
      width: '300px',
      enterAnimationDuration: 500,
      exitAnimationDuration: 1000,
      data: {
        badgeNumber: badgeNumber,
        timeclockStatus: timeclockStatus,
      },
    });

    dialogRef.afterOpened().subscribe((result) => {
      setTimeout(() => {
        dialogRef.close();
      }, 3500);
    });
  }

  /**
   * Open the dialog to display timeclock history
   * @param badgeNumber The employee badge number
   */
  openHistoryDialog(badgeNumber: string): void {
    this.dialog.open(TimeclockHistoryDialog, {
      width: '1000px',
      maxWidth: '95vw',
      maxHeight: '90vh',
      data: {
        badgeNumber: badgeNumber,
      },
    });
  }
}

@Component({
  selector: 'app-timeclock-dialog',
  templateUrl: './timeclock-dialog.html',
  styleUrl: './timeclock-dialog.scss',
  standalone: true,
  imports: [MatDialogTitle, MatDialogContent, MatIconModule],
})
export class TimeclockDialog {
  readonly data = inject(MAT_DIALOG_DATA);
}

@Component({
  selector: 'app-timeclock-history-dialog',
  templateUrl: './timeclock-history-dialog.html',
  styleUrl: './timeclock-history-dialog.scss',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatIconModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatProgressSpinnerModule,
  ],
})
export class TimeclockHistoryDialog implements OnInit {
  readonly data = inject(MAT_DIALOG_DATA);
  readonly dialogRef = inject(MatDialog);
  private timeclockService = inject(TimeclockService);
  readonly errorDialog = inject(ErrorDialogComponent);

  currentMonth: Date = new Date();
  calendarDays: CalendarDay[] = [];
  allEntries: TimeclockEntry[] = [];
  earliestEntry: Date | null = null;
  isLoading = false;
  showMonthYearPicker = false;
  selectedMonthYear: Date = new Date();

  canGoPrevious = true;
  canGoNext = false;

  ngOnInit() {
    this.loadAllHistory();
  }

  loadAllHistory() {
    this.isLoading = true;

    // Load from earliest possible date to today
    const endDate = new Date();
    const startDate = new Date(2020, 0, 1); // Start from Jan 1, 2020

    this.timeclockService
      .getEmployeeHistory(this.data.badgeNumber, startDate, endDate)
      .subscribe({
        next: (entries) => {
          this.allEntries = entries;

          // Find earliest entry
          if (entries.length > 0) {
            const earliest = entries.reduce((min, entry) => {
              const entryDate = new Date(entry.clock_in);
              return entryDate < min ? entryDate : min;
            }, new Date(entries[0].clock_in));
            this.earliestEntry = new Date(
              earliest.getFullYear(),
              earliest.getMonth(),
              1,
            );
          }

          this.generateCalendar();
          this.updateNavigationState();
          this.isLoading = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog(
            'Failed to load timeclock history',
            error,
          );
          this.isLoading = false;
        },
      });
  }

  generateCalendar() {
    const year = this.currentMonth.getFullYear();
    const month = this.currentMonth.getMonth();

    // First day of the month
    const firstDay = new Date(year, month, 1);
    const firstDayOfWeek = firstDay.getDay();

    // Last day of the month
    const lastDay = new Date(year, month + 1, 0);
    const lastDate = lastDay.getDate();

    // Calculate the start date (may be in previous month)
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDayOfWeek);

    // Generate all days
    this.calendarDays = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 0; i < 42; i++) {
      // 6 weeks max
      const currentDate = new Date(startDate);
      currentDate.setDate(startDate.getDate() + i);

      const isCurrentMonth = currentDate.getMonth() === month;
      const isToday = currentDate.getTime() === today.getTime();

      // Find entries for this day
      const dayEntries = this.allEntries.filter((entry) => {
        const entryDate = new Date(entry.clock_in);
        entryDate.setHours(0, 0, 0, 0);
        return entryDate.getTime() === currentDate.getTime();
      });

      this.calendarDays.push({
        date: new Date(currentDate),
        isCurrentMonth,
        isToday,
        entries: dayEntries,
      });
    }
  }

  previousMonth() {
    this.currentMonth = new Date(
      this.currentMonth.getFullYear(),
      this.currentMonth.getMonth() - 1,
      1,
    );
    this.generateCalendar();
    this.updateNavigationState();
  }

  nextMonth() {
    this.currentMonth = new Date(
      this.currentMonth.getFullYear(),
      this.currentMonth.getMonth() + 1,
      1,
    );
    this.generateCalendar();
    this.updateNavigationState();
  }

  updateNavigationState() {
    const now = new Date();
    const currentMonthStart = new Date(now.getFullYear(), now.getMonth(), 1);

    // Can't go forward past current month
    this.canGoNext = this.currentMonth < currentMonthStart;

    // Can't go back before earliest entry
    if (this.earliestEntry) {
      this.canGoPrevious = this.currentMonth > this.earliestEntry;
    } else {
      this.canGoPrevious = true;
    }
  }

  openMonthYearPicker() {
    this.showMonthYearPicker = !this.showMonthYearPicker;
    this.selectedMonthYear = new Date(this.currentMonth);
  }

  onMonthYearSelected(event: any) {
    const selectedDate = event.value || event;
    if (selectedDate) {
      this.currentMonth = new Date(
        selectedDate.getFullYear(),
        selectedDate.getMonth(),
        1,
      );
      this.generateCalendar();
      this.updateNavigationState();
      this.showMonthYearPicker = false;
    }
  }

  calculateDuration(clockIn: string, clockOut: string): string {
    const start = new Date(clockIn);
    const end = new Date(clockOut);
    const durationMs = end.getTime() - start.getTime();
    const hours = Math.floor(durationMs / (1000 * 60 * 60));
    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  close() {
    this.dialogRef.closeAll();
  }
}
