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
    'last_seen',
    'is_active',
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

  async ngOnInit() {
    this.loadDevices();
    await this.verifyCurrentBrowser();
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

  async verifyCurrentBrowser() {
    try {
      const fingerprint = await this.deviceUuidService.generateFingerprint();
      const storedUuid = this.deviceUuidService.getDeviceUuid();

      this.deviceService
        .verifyBrowser({
          fingerprint_hash: fingerprint,
          browser_uuid: storedUuid || undefined,
        })
        .subscribe({
          next: (response) => {
            if (response.verified && response.browser_uuid) {
              this.currentBrowserUuid = response.browser_uuid;
              this.currentBrowserName = response.browser_name || null;

              // If UUID was restored from fingerprint, update localStorage
              if (response.restored) {
                this.deviceUuidService.setDeviceUuid(
                  response.browser_uuid,
                  response.browser_name
                );
                this.showSnackBar(
                  'Device registration restored',
                  'success'
                );
              }

              this.checkIfCurrentBrowserIsRegistered();
            } else {
              this.currentBrowserUuid = storedUuid;
              this.currentBrowserName =
                this.deviceUuidService.getBrowserName();
              this.checkIfCurrentBrowserIsRegistered();
            }
          },
          error: (error) => {
            console.error('Fingerprint verification failed:', error);
            this.currentBrowserUuid = storedUuid;
            this.currentBrowserName = this.deviceUuidService.getBrowserName();
            this.checkIfCurrentBrowserIsRegistered();
          },
        });
    } catch (error) {
      console.error('Failed to generate fingerprint:', error);
      this.currentBrowserUuid = this.deviceUuidService.getDeviceUuid();
      this.currentBrowserName = this.deviceUuidService.getBrowserName();
      this.checkIfCurrentBrowserIsRegistered();
    }
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

  async registerDevice() {
    if (this.registerForm.valid) {
      this.isRegistering = true;

      try {
        const fingerprint =
          await this.deviceUuidService.generateFingerprint();
        const browserData = {
          ...this.registerForm.value,
          fingerprint_hash: fingerprint,
          user_agent: navigator.userAgent,
        };

        this.deviceService.registerDevice(browserData).subscribe({
          next: (browser) => {
            // Save the UUID and name to localStorage for this browser
            this.deviceUuidService.setDeviceUuid(
              browser.browser_uuid,
              browser.browser_name
            );
            this.currentBrowserUuid = browser.browser_uuid;
            this.currentBrowserName = browser.browser_name;

            this.showSnackBar('Device registered successfully', 'success');
            this.registerForm.reset();
            this.loadDevices();
            this.isRegistering = false;
          },
          error: (error) => {
            this.errorDialog.openErrorDialog(
              'Failed to register device',
              error
            );
            this.isRegistering = false;
          },
        });
      } catch (error) {
        this.errorDialog.openErrorDialog(
          'Failed to generate device fingerprint',
          error
        );
        this.isRegistering = false;
      }
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

  async useCurrentBrowserUuid() {
    if (this.currentBrowserUuid && this.currentBrowserName) {
      try {
        const fingerprint =
          await this.deviceUuidService.generateFingerprint();
        const browserData = {
          browser_uuid: this.currentBrowserUuid,
          browser_name: this.currentBrowserName,
          fingerprint_hash: fingerprint,
          user_agent: navigator.userAgent,
        };

        this.isRegistering = true;
        this.deviceService.registerDevice(browserData).subscribe({
          next: () => {
            this.showSnackBar('Device reregistered successfully', 'success');
            this.loadDevices();
            this.isRegistering = false;
          },
          error: (error) => {
            this.errorDialog.openErrorDialog(
              'Failed to reregister device',
              error
            );
            this.isRegistering = false;
          },
        });
      } catch (error) {
        this.errorDialog.openErrorDialog(
          'Failed to generate device fingerprint',
          error
        );
      }
    } else {
      this.showSnackBar('No device registration found', 'info');
    }
  }

  clearBrowserUuid() {
    if (confirm('Are you sure you want to unregister this device?')) {
      this.deviceUuidService.clearDeviceUuid();
      this.currentBrowserUuid = null;
      this.currentBrowserName = null;
      this.isCurrentBrowserRegistered = false;
      this.showSnackBar('Device unregistered', 'success');
    }
  }

  generateDeviceUUID() {
    // Generate a human-readable UUID in format WORD-WORD-WORD-NUMBER
    const wordList = [
      'APPLE', 'BEACH', 'CLOUD', 'DELTA', 'EAGLE', 'FLAME', 'GRASS', 'HOUSE',
      'IVORY', 'JADE', 'KITE', 'LIGHT', 'MOON', 'NIGHT', 'OCEAN', 'PEARL',
      'QUIET', 'RIVER', 'STONE', 'TIGER', 'ULTRA', 'VENUS', 'WATER', 'XENON',
      'YOUTH', 'ZEBRA', 'AMBER', 'BLADE', 'CEDAR', 'DUNE', 'EMBER', 'FROST',
      'GROVE', 'HAWK', 'IRIS', 'JET', 'KING', 'LOTUS', 'MIST', 'NOVA',
      'OPAL', 'PINE', 'QUARTZ', 'RAVEN', 'SAGE', 'THORN', 'UNITY', 'VINE',
      'WOLF', 'XRAY', 'YELLOW', 'ZINC', 'ARCTIC', 'BLAZE', 'CORAL', 'DAWN',
      'ECHO', 'FLARE', 'GLOW', 'HALO', 'ICE', 'JADE', 'KELP', 'LAVA',
      'MAPLE', 'NECTAR', 'ORBIT', 'PRISM', 'QUEST', 'RIDGE', 'SOLAR', 'TIDE',
      'URBAN', 'VORTEX', 'WHALE', 'XYLEM', 'YARN', 'ZENITH', 'AZURE', 'BRICK',
      'CRISP', 'DREAM', 'EDGE', 'FIELD', 'GRAIN', 'HAVEN', 'ISLAND', 'JEWEL',
      'KNIGHT', 'LAKE', 'MEADOW', 'NORTH', 'OLIVE', 'PLAIN', 'QUEST', 'RANGE',
      'SLOPE', 'TRAIL', 'UNION', 'VALLEY', 'WAVE', 'YIELD', 'ZONE', 'ARCH',
      'BOLT', 'CAPE', 'DRIFT', 'EARTH', 'FLASH', 'GATE', 'HAVEN', 'INLET',
      'JADE', 'KNOT', 'LEAF', 'MOUNT', 'NORTH', 'ORBIT', 'PEAK', 'QUIET',
      'ROCKY', 'SHORE', 'TOWER', 'UPPER', 'VISTA', 'WEST', 'YACHT', 'ZEAL'
    ];

    // Select 3 random words
    const shuffled = [...wordList].sort(() => Math.random() - 0.5);
    const words = shuffled.slice(0, 3);

    // Generate a random number between 10 and 99
    const number = Math.floor(Math.random() * 90) + 10;

    // Combine into UUID format
    const uuid = `${words[0]}-${words[1]}-${words[2]}-${number}`;
    this.registerForm.patchValue({ browser_uuid: uuid });
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
