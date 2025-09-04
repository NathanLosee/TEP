import { DatePipe } from '@angular/common';
import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogContent,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatToolbarModule } from '@angular/material/toolbar';
import { interval, Subscription } from 'rxjs';
import { TimeclockService } from '../../services/timeclock.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

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
  ],
  templateUrl: './timeclock.component.html',
  styleUrl: './timeclock.component.scss',
})
export class TimeclockComponent implements OnInit, OnDestroy {
  private timeclockService = inject(TimeclockService);
  private clockSubscription?: Subscription;
  readonly dialog = inject(MatDialog);
  readonly errorDialog = inject(ErrorDialogComponent);

  currentDateAndTime = Date.now();
  badgeNumber: string;

  constructor() {
    this.badgeNumber = '';
  }

  ngOnInit() {
    // Update the current date and time every minute
    const timer = interval(60000);
    this.clockSubscription = timer.subscribe(() => {
      this.currentDateAndTime = Date.now();
    });
  }

  ngOnDestroy() {
    // Unsubscribe from the timer to prevent memory leaks
    if (this.clockSubscription) {
      this.clockSubscription.unsubscribe();
    }
  }

  /**
   * Clock in/out for the employee ID
   */
  clockInOut() {
    this.timeclockService.timeclock(this.badgeNumber).subscribe({
      next: (response) => {
        console.log(response);
        this.openTimeclockDialog(this.badgeNumber, response.message);
        this.badgeNumber = '';
      },
      error: (error) => {
        this.errorDialog.openErrorDialog('Failed to clock in/out', error);
      },
    });
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
}

@Component({
  selector: 'app-timeclock-dialog',
  templateUrl: './timeclock-dialog.html',
  styleUrl: './timeclock-dialog.scss',
  standalone: true,
  imports: [MatDialogTitle, MatDialogContent],
})
export class TimeclockDialog {
  readonly data = inject(MAT_DIALOG_DATA);
}
