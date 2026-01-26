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
import { MatTooltipModule } from '@angular/material/tooltip';
import { SystemSettingsService, SystemSettings } from '../../services/system-settings.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

@Component({
  selector: 'app-system-settings',
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
    MatTooltipModule,
  ],
  templateUrl: './system-settings.component.html',
  styleUrl: './system-settings.component.scss'
})
export class SystemSettingsComponent implements OnInit {
  private settingsService = inject(SystemSettingsService);
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  readonly errorDialog = inject(ErrorDialogComponent);

  settingsForm: FormGroup;
  settings: SystemSettings | null = null;
  isLoading = false;
  isSaving = false;
  isUploadingLogo = false;
  selectedLogoFile: File | null = null;
  logoPreviewUrl: string | null = null;
  logoCacheBuster = Date.now();

  // Default colors matching Angular Material M3 dark theme with mat.$green-palette and mat.$yellow-palette
  // These values match --sys-primary, --sys-secondary, and --sys-tertiary from the compiled theme
  static readonly DEFAULT_PRIMARY = '#02E600';    // --sys-primary from mat.$green-palette
  static readonly DEFAULT_SECONDARY = '#BBCBB2';  // --sys-secondary from mat.$green-palette
  static readonly DEFAULT_ACCENT = '#CDCD00';     // --sys-tertiary from mat.$yellow-palette

  constructor() {
    this.settingsForm = this.fb.group({
      primary_color: [SystemSettingsComponent.DEFAULT_PRIMARY, [Validators.required, Validators.pattern(/^#[0-9A-Fa-f]{6}$/)]],
      secondary_color: [SystemSettingsComponent.DEFAULT_SECONDARY, [Validators.required, Validators.pattern(/^#[0-9A-Fa-f]{6}$/)]],
      accent_color: [SystemSettingsComponent.DEFAULT_ACCENT, [Validators.required, Validators.pattern(/^#[0-9A-Fa-f]{6}$/)]],
    });
  }

  ngOnInit() {
    this.loadSettings();
  }

  loadSettings() {
    this.isLoading = true;
    this.settingsService.getSettings().subscribe({
      next: (settings) => {
        this.settings = settings;
        this.settingsForm.patchValue({
          primary_color: settings.primary_color,
          secondary_color: settings.secondary_color,
          accent_color: settings.accent_color,
        });
        this.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog('Failed to load settings', error);
        this.isLoading = false;
      }
    });
  }

  saveSettings() {
    if (this.settingsForm.valid) {
      this.isSaving = true;
      this.settingsService.updateSettings(this.settingsForm.value).subscribe({
        next: (settings) => {
          this.settings = settings;
          this.settingsService.applyTheme(settings);
          this.showSnackBar('Settings saved successfully', 'success');
          this.isSaving = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to save settings', error);
          this.isSaving = false;
        }
      });
    }
  }

  onLogoFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];

      // Validate file type
      const allowedTypes = ['image/png', 'image/jpeg', 'image/svg+xml'];
      if (!allowedTypes.includes(file.type)) {
        this.showSnackBar('Invalid file type. Allowed: PNG, JPG, SVG', 'error');
        return;
      }

      // Validate file size (2MB max)
      if (file.size > 2 * 1024 * 1024) {
        this.showSnackBar('File too large. Maximum size is 2MB', 'error');
        return;
      }

      this.selectedLogoFile = file;

      // Create preview URL
      this.logoPreviewUrl = URL.createObjectURL(file);
    }
  }

  uploadLogo() {
    if (this.selectedLogoFile) {
      this.isUploadingLogo = true;
      this.settingsService.uploadLogo(this.selectedLogoFile).subscribe({
        next: (settings) => {
          this.settings = settings;
          this.selectedLogoFile = null;
          if (this.logoPreviewUrl) {
            URL.revokeObjectURL(this.logoPreviewUrl);
            this.logoPreviewUrl = null;
          }
          // Update cache buster to force reload of logo image
          this.logoCacheBuster = Date.now();
          this.showSnackBar('Logo uploaded successfully', 'success');
          this.isUploadingLogo = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to upload logo', error);
          this.isUploadingLogo = false;
        }
      });
    }
  }

  deleteLogo() {
    if (confirm('Are you sure you want to delete the logo?')) {
      this.settingsService.deleteLogo().subscribe({
        next: () => {
          if (this.settings) {
            this.settings = { ...this.settings, has_logo: false, logo_filename: null };
          }
          this.showSnackBar('Logo deleted', 'success');
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to delete logo', error);
        }
      });
    }
  }

  cancelLogoUpload() {
    this.selectedLogoFile = null;
    if (this.logoPreviewUrl) {
      URL.revokeObjectURL(this.logoPreviewUrl);
      this.logoPreviewUrl = null;
    }
  }

  getLogoUrl(): string {
    return this.settingsService.getLogoUrl(this.logoCacheBuster);
  }

  resetToDefaults() {
    if (confirm('Are you sure you want to reset colors to defaults?')) {
      this.settingsForm.patchValue({
        primary_color: SystemSettingsComponent.DEFAULT_PRIMARY,
        secondary_color: SystemSettingsComponent.DEFAULT_SECONDARY,
        accent_color: SystemSettingsComponent.DEFAULT_ACCENT,
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
