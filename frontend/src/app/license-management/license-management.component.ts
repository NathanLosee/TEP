import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { LicenseService, LicenseStatus } from '../../services/license.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

@Component({
  selector: 'app-license-management',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
  ],
  templateUrl: './license-management.component.html',
  styleUrl: './license-management.component.scss'
})
export class LicenseManagementComponent implements OnInit {
  private licenseService = inject(LicenseService);
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  readonly errorDialog = inject(ErrorDialogComponent);

  licenseForm: FormGroup;
  licenseStatus: LicenseStatus | null = null;
  isLoading = false;
  isActivating = false;

  constructor() {
    this.licenseForm = this.fb.group({
      license_key: ['', [Validators.required, Validators.minLength(128), Validators.maxLength(128), Validators.pattern(/^[0-9a-fA-F]{128}$/)]],
    });
  }

  ngOnInit() {
    this.loadLicenseStatus();
  }

  loadLicenseStatus() {
    this.isLoading = true;
    this.licenseService.getLicenseStatus().subscribe({
      next: (status) => {
        this.licenseStatus = status;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog('Failed to load license status', error);
        this.isLoading = false;
      }
    });
  }

  activateLicense() {
    if (this.licenseForm.valid) {
      this.isActivating = true;
      const formValue = this.licenseForm.value;

      this.licenseService.activateLicense(
        formValue.license_key.toLowerCase()
      ).subscribe({
        next: () => {
          this.showSnackBar('License activated successfully', 'success');
          this.licenseForm.reset();
          this.loadLicenseStatus();
          this.isActivating = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to activate license', error);
          this.isActivating = false;
        }
      });
    }
  }

  deactivateLicense() {
    if (confirm('Are you sure you want to deactivate the current license? This will lock all admin features.')) {
      this.isActivating = true;
      this.licenseService.deactivateLicense().subscribe({
        next: () => {
          this.showSnackBar('License deactivated', 'success');
          this.loadLicenseStatus();
          this.isActivating = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to deactivate license', error);
          this.isActivating = false;
        }
      });
    }
  }

  private showSnackBar(message: string, type: 'success' | 'error' | 'info' = 'info') {
    this.snackBar.open(message, 'Close', {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }
}
