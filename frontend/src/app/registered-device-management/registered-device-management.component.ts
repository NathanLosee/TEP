import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
  RegisteredDevice,
  RegisteredDeviceService,
} from '../../services/registered-device.service';
import { DeviceUuidService } from '../../services/device-uuid.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { DisableIfNoPermissionDirective } from '../directives/has-permission.directive';

@Component({
  selector: 'app-registered-device-management',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatCheckboxModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDialogModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    DisableIfNoPermissionDirective,
  ],
  templateUrl: './registered-device-management.component.html',
  styleUrl: './registered-device-management.component.scss',
})
export class RegisteredDeviceManagementComponent implements OnInit {
  private deviceService = inject(RegisteredDeviceService);
  private deviceUuidService = inject(DeviceUuidService);
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);
  readonly errorDialog = inject(ErrorDialogComponent);

  devices: RegisteredDevice[] = [];
  displayedColumns: string[] = [
    'browser_name',
    'browser_uuid',
    'actions',
  ];

  registerForm: FormGroup;
  isLoading = false;
  isRegistering = false;
  currentBrowserUuid: string | null = null;
  currentBrowserName: string | null = null;
  isCurrentBrowserRegistered = false;

  constructor() {
    this.registerForm = this.fb.group({
      browser_name: ['', [Validators.required, Validators.minLength(3)]],
      browser_uuid: ['', [Validators.required]],
    });
  }

  ngOnInit() {
    this.loadDevices();
    this.currentBrowserUuid = this.deviceUuidService.getDeviceUuid();
    this.currentBrowserName = this.deviceUuidService.getBrowserName();
  }

  loadDevices() {
    this.isLoading = true;
    this.deviceService.getAllDevices().subscribe({
      next: (devices) => {
        this.devices = devices;
        this.checkIfCurrentBrowserIsRegistered();
        this.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog('Failed to load devices', error);
        this.isLoading = false;
      },
    });
  }

  checkIfCurrentBrowserIsRegistered() {
    if (this.currentBrowserUuid) {
      this.isCurrentBrowserRegistered = this.devices.some(
        (browser) => browser.browser_uuid === this.currentBrowserUuid
      );
    } else {
      this.isCurrentBrowserRegistered = false;
    }
  }

  registerDevice() {
    if (this.registerForm.valid) {
      this.isRegistering = true;
      const browserData = this.registerForm.value;

      this.deviceService.registerDevice(browserData).subscribe({
        next: (browser) => {
          // Save the UUID and name to localStorage for this browser
          this.deviceUuidService.setDeviceUuid(browser.browser_uuid, browser.browser_name);
          this.currentBrowserUuid = browser.browser_uuid;
          this.currentBrowserName = browser.browser_name;

          this.showSnackBar('Browser registered successfully', 'success');
          this.registerForm.reset();
          this.loadDevices();
          this.isRegistering = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to register browser', error);
          this.isRegistering = false;
        },
      });
    }
  }

  deleteDevice(browser: RegisteredDevice) {
    if (confirm(`Are you sure you want to revoke "${browser.browser_name}"?`)) {
      this.deviceService.deleteDevice(browser.id).subscribe({
        next: () => {
          // If deleting the current browser's registration, clear localStorage
          if (browser.browser_uuid === this.currentBrowserUuid) {
            this.deviceUuidService.clearDeviceUuid();
            this.currentBrowserUuid = null;
            this.currentBrowserName = null;
          }

          this.showSnackBar('Browser revoked successfully', 'success');
          this.loadDevices();
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to revoke browser', error);
        },
      });
    }
  }

  useCurrentBrowserUuid() {
    if (this.currentBrowserUuid && this.currentBrowserName) {
      // Send a registration request with the current browser info
      const browserData = {
        browser_uuid: this.currentBrowserUuid,
        browser_name: this.currentBrowserName
      };

      this.isRegistering = true;
      this.deviceService.registerDevice(browserData).subscribe({
        next: () => {
          this.showSnackBar('Browser reregistered successfully', 'success');
          this.loadDevices();
          this.isRegistering = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to reregister browser', error);
          this.isRegistering = false;
        },
      });
    } else {
      this.showSnackBar('No browser registration found', 'info');
    }
  }

  clearBrowserUuid() {
    if (confirm('Are you sure you want to unregister this browser?')) {
      this.deviceUuidService.clearDeviceUuid();
      this.currentBrowserUuid = null;
      this.currentBrowserName = null;
      this.isCurrentBrowserRegistered = false;
      this.showSnackBar('Browser unregistered', 'success');
    }
  }

  generateDeviceUUID() {
    // Generate a simple UUID-like string for demonstration
    const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(
      /[xy]/g,
      function (c) {
        const r = (Math.random() * 16) | 0,
          v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      }
    );
    this.registerForm.patchValue({ device_uuid: uuid });
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
