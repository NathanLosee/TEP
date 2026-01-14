import { Component, inject, Injectable } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
  MatDialogTitle,
} from '@angular/material/dialog';
import { HttpErrorResponse } from '@angular/common/http';

export interface ErrorDetail {
  detail?: string;
  message?: string;
}

export type AppError = string | HttpErrorResponse | { error: ErrorDetail } | Error;

@Injectable({
  providedIn: 'root',
})
export class ErrorDialogComponent {
  readonly dialog = inject(MatDialog);

  /**
   * Open the dialog to display the error message
   * @param msg Context message about where the error occurred
   * @param error The error object (string, HttpErrorResponse, or Error)
   */
  openErrorDialog(msg: string, error: AppError): void {
    console.error(msg, error);

    let errorMessage: string;
    if (typeof error === 'string') {
      errorMessage = error;
    } else if (error instanceof HttpErrorResponse) {
      errorMessage = error.error?.detail || error.message || 'An error occurred';
    } else if ('error' in error && error.error) {
      errorMessage = error.error.detail || error.error.message || 'An error occurred';
    } else if (error instanceof Error) {
      errorMessage = error.message;
    } else {
      errorMessage = 'An unknown error occurred';
    }

    this.dialog.open(ErrorDialog, {
      height: '300px',
      width: '300px',
      enterAnimationDuration: 250,
      exitAnimationDuration: 1000,
      data: { errorMessage },
      panelClass: 'error-dialog',
    });
  }
}

@Component({
  selector: 'app-error-dialog',
  standalone: true,
  imports: [
    MatButtonModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatDialogClose,
  ],
  templateUrl: './error-dialog.component.html',
  styleUrl: './error-dialog.component.scss',
})
export class ErrorDialog {
  readonly data = inject(MAT_DIALOG_DATA);
}
