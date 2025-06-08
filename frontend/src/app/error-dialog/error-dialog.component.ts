import { Component, Inject, inject, Injectable } from '@angular/core';
import {
  MatDialog,
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogContent,
  MatDialogClose,
  MatDialogTitle,
} from '@angular/material/dialog';

@Injectable({
  providedIn: 'root',
})
export class ErrorDialogComponent {
  readonly dialog = inject(MatDialog);

  /**
   * Open the dialog to display the error message
   * @param errorMessage The error message to display
   */
  openErrorDialog(error: any): void {
    console.error('Error:', error);
    this.dialog.open(ErrorDialog, {
      height: '300px',
      width: '300px',
      enterAnimationDuration: 250,
      exitAnimationDuration: 1000,
      data: {
        errorMessage: typeof error === 'string' ? error : error.error.detail,
      },
      panelClass: 'error-dialog',
    });
  }
}

@Component({
  selector: 'app-error-dialog',
  standalone: true,
  imports: [MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose],
  templateUrl: './error-dialog.component.html',
  styleUrl: './error-dialog.component.scss',
})
export class ErrorDialog {
  readonly data = inject(MAT_DIALOG_DATA);
}
