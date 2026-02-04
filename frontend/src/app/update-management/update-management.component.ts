import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil, interval } from 'rxjs';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

import { UpdateService, UpdateStatus, ReleaseInfo } from '../../services/update.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

@Component({
  selector: 'app-update-management',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatChipsModule,
    MatDialogModule,
  ],
  templateUrl: './update-management.component.html',
  styleUrl: './update-management.component.scss'
})
export class UpdateManagementComponent implements OnInit, OnDestroy {
  private updateService = inject(UpdateService);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);
  readonly errorDialog = inject(ErrorDialogComponent);
  private destroy$ = new Subject<void>();

  status: UpdateStatus | null = null;
  releaseInfo: ReleaseInfo | null = null;
  isLoading = true;
  isChecking = false;
  isDownloading = false;
  isApplying = false;
  isRollingBack = false;

  ngOnInit(): void {
    this.loadStatus();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadStatus(): void {
    this.isLoading = true;
    this.updateService.getStatus().subscribe({
      next: (status) => {
        this.status = status;
        this.isLoading = false;
        if (status.state === 'downloading') {
          this.startPolling();
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.errorDialog.openErrorDialog('Failed to load update status', err);
      }
    });
  }

  checkForUpdate(): void {
    this.isChecking = true;
    this.updateService.checkForUpdate().subscribe({
      next: (release) => {
        this.releaseInfo = release;
        this.isChecking = false;
        this.loadStatus();
        this.snackBar.open(
          `Update available: v${release.version}`,
          'Dismiss',
          { duration: 4000, panelClass: ['snackbar-info'] }
        );
      },
      error: (err) => {
        this.isChecking = false;
        if (err.status === 204) {
          this.loadStatus();
          this.snackBar.open(
            'You are running the latest version',
            'Dismiss',
            { duration: 4000, panelClass: ['snackbar-info'] }
          );
        } else {
          this.errorDialog.openErrorDialog('Failed to check for updates', err);
        }
      }
    });
  }

  downloadUpdate(): void {
    this.isDownloading = true;
    this.startPolling();
    this.updateService.downloadUpdate().subscribe({
      next: () => {
        this.isDownloading = false;
        this.loadStatus();
        this.snackBar.open(
          'Update downloaded successfully',
          'Dismiss',
          { duration: 4000, panelClass: ['snackbar-success'] }
        );
      },
      error: (err) => {
        this.isDownloading = false;
        this.errorDialog.openErrorDialog('Failed to download update', err);
        this.loadStatus();
      }
    });
  }

  applyUpdate(): void {
    const confirmed = confirm(
      'Apply this update? The server will restart and be briefly unavailable.'
    );
    if (!confirmed) return;

    this.isApplying = true;
    this.updateService.applyUpdate().subscribe({
      next: () => {
        this.snackBar.open(
          'Update is being applied. The server will restart.',
          'Dismiss',
          { duration: 10000, panelClass: ['snackbar-info'] }
        );
      },
      error: (err) => {
        this.isApplying = false;
        this.errorDialog.openErrorDialog('Failed to apply update', err);
      }
    });
  }

  rollback(): void {
    const confirmed = confirm(
      'Rollback to the previous version? The server will restart.'
    );
    if (!confirmed) return;

    this.isRollingBack = true;
    this.updateService.rollbackUpdate().subscribe({
      next: () => {
        this.snackBar.open(
          'Rollback in progress. The server will restart.',
          'Dismiss',
          { duration: 10000, panelClass: ['snackbar-info'] }
        );
      },
      error: (err) => {
        this.isRollingBack = false;
        this.errorDialog.openErrorDialog('Failed to rollback', err);
      }
    });
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  formatDate(dateStr: string | null): string {
    if (!dateStr) return 'Never';
    return new Date(dateStr).toLocaleString();
  }

  private startPolling(): void {
    interval(2000)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.updateService.getStatus().subscribe({
          next: (status) => {
            this.status = status;
            if (status.state !== 'downloading') {
              this.destroy$.next();
            }
          }
        });
      });
  }
}
