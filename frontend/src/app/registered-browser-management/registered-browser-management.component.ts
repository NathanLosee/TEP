import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { BrowserUuidService } from '../../services/browser-uuid.service';
import {
  RegisteredBrowser,
  RegisteredBrowserService,
} from '../../services/registered-browser.service';
import { DisableIfNoPermissionDirective } from '../directives/has-permission.directive';
import {
  AppError,
  ErrorDialogComponent,
} from '../error-dialog/error-dialog.component';
import {
  GenericTableComponent,
  TableCellDirective,
} from '../shared/components/generic-table';
import {
  TableAction,
  TableActionEvent,
  TableColumn,
} from '../shared/models/table.models';

@Component({
  selector: 'app-registered-browser-management',
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
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    DisableIfNoPermissionDirective,
    GenericTableComponent,
    TableCellDirective,
  ],
  templateUrl: './registered-browser-management.component.html',
  styleUrl: './registered-browser-management.component.scss',
})
export class RegisteredBrowserManagementComponent implements OnInit {
  private browserService = inject(RegisteredBrowserService);
  private browserUuidService = inject(BrowserUuidService);
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  readonly errorDialog = inject(ErrorDialogComponent);

  browsers: RegisteredBrowser[] = [];

  // Table configuration
  columns: TableColumn<RegisteredBrowser>[] = [
    {
      key: 'browser_name',
      header: 'Browser Name',
      type: 'icon-text',
      icon: 'computer',
    },
    {
      key: 'browser_uuid',
      header: 'Browser UUID',
      type: 'template',
    },
    {
      key: 'last_seen',
      header: 'Last Seen',
      type: 'date',
      dateFormat: 'short',
    },
    {
      key: 'is_active',
      header: 'Status',
      type: 'template',
    },
  ];

  actions: TableAction<RegisteredBrowser>[] = [
    {
      icon: 'delete',
      tooltip: 'Revoke Browser',
      action: 'delete',
      color: 'warn',
      permission: 'registered_browser.delete',
    },
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
    this.loadBrowsers();
    await this.verifyCurrentBrowser();
  }

  loadBrowsers() {
    this.isLoading = true;
    this.browserService.getAllBrowsers().subscribe({
      next: (browsers) => {
        this.browsers = browsers;
        this.checkIfCurrentBrowserIsRegistered();
        this.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog('Failed to load browsers', error);
        this.isLoading = false;
      },
    });
  }

  async verifyCurrentBrowser() {
    try {
      const fingerprint = await this.browserUuidService.generateFingerprint();
      const storedUuid = this.browserUuidService.getBrowserUuid();

      this.browserService
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
                this.browserUuidService.setBrowserUuid(
                  response.browser_uuid,
                  response.browser_name
                );
                this.showSnackBar(
                  'Browser registration restored',
                  'success'
                );
              }

              this.checkIfCurrentBrowserIsRegistered();
            } else {
              this.currentBrowserUuid = storedUuid;
              this.currentBrowserName =
                this.browserUuidService.getBrowserName();
              this.checkIfCurrentBrowserIsRegistered();
            }
          },
          error: (error) => {
            this.currentBrowserUuid = storedUuid;
            this.currentBrowserName = this.browserUuidService.getBrowserName();
            this.checkIfCurrentBrowserIsRegistered();
          },
        });
    } catch (error) {
      this.currentBrowserUuid = this.browserUuidService.getBrowserUuid();
      this.currentBrowserName = this.browserUuidService.getBrowserName();
      this.checkIfCurrentBrowserIsRegistered();
    }
  }

  checkIfCurrentBrowserIsRegistered() {
    if (this.currentBrowserUuid) {
      this.isCurrentBrowserRegistered = this.browsers.some(
        (browser) => browser.browser_uuid === this.currentBrowserUuid
      );
    } else {
      this.isCurrentBrowserRegistered = false;
    }
  }

  onTableAction(event: TableActionEvent<RegisteredBrowser>) {
    switch (event.action) {
      case 'delete':
        this.deleteBrowser(event.row);
        break;
    }
  }

  async registerBrowser() {
    if (this.registerForm.valid) {
      this.isRegistering = true;

      try {
        const fingerprint =
          await this.browserUuidService.generateFingerprint();
        const browserData = {
          ...this.registerForm.value,
          fingerprint_hash: fingerprint,
          user_agent: navigator.userAgent,
        };

        this.browserService.registerBrowser(browserData).subscribe({
          next: (browser) => {
            // Save the UUID and name to localStorage for this browser
            this.browserUuidService.setBrowserUuid(
              browser.browser_uuid,
              browser.browser_name
            );
            this.currentBrowserUuid = browser.browser_uuid;
            this.currentBrowserName = browser.browser_name;

            this.showSnackBar('Browser registered successfully', 'success');
            this.registerForm.reset();
            this.loadBrowsers();
            this.isRegistering = false;
          },
          error: (error) => {
            this.errorDialog.openErrorDialog(
              'Failed to register browser',
              error
            );
            this.isRegistering = false;
          },
        });
      } catch (error) {
        this.errorDialog.openErrorDialog(
          'Failed to generate browser fingerprint',
          error as AppError
        );
        this.isRegistering = false;
      }
    }
  }

  deleteBrowser(browser: RegisteredBrowser) {
    if (confirm(`Are you sure you want to revoke "${browser.browser_name}"?`)) {
      this.browserService.deleteBrowser(browser.id).subscribe({
        next: () => {
          // If deleting the current browser's registration, clear localStorage
          if (browser.browser_uuid === this.currentBrowserUuid) {
            this.browserUuidService.clearBrowserUuid();
            this.currentBrowserUuid = null;
            this.currentBrowserName = null;
          }

          this.showSnackBar('Browser revoked successfully', 'success');
          this.loadBrowsers();
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to revoke browser', error);
        },
      });
    }
  }

  clearBrowserUuid() {
    if (confirm('Are you sure you want to unregister this browser?')) {
      this.browserUuidService.clearBrowserUuid();
      this.currentBrowserUuid = null;
      this.currentBrowserName = null;
      this.isCurrentBrowserRegistered = false;
      this.showSnackBar('Browser unregistered', 'success');
    }
  }

  generateBrowserUUID() {
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
