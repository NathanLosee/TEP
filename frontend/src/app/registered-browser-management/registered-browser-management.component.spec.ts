import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { RegisteredBrowserManagementComponent } from './registered-browser-management.component';
import { RegisteredBrowserService, RegisteredBrowser, RegisteredBrowserCreate } from '../../services/registered-browser.service';
import { BrowserUuidService } from '../../services/browser-uuid.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

describe('RegisteredBrowserManagementComponent', () => {
  let component: RegisteredBrowserManagementComponent;
  let fixture: ComponentFixture<RegisteredBrowserManagementComponent>;
  let mockBrowserService: jasmine.SpyObj<RegisteredBrowserService>;
  let mockBrowserUuidService: jasmine.SpyObj<BrowserUuidService>;
  let mockSnackBar: jasmine.SpyObj<MatSnackBar>;
  let mockErrorDialog: jasmine.SpyObj<ErrorDialogComponent>;

  const mockBrowsers: RegisteredBrowser[] = [
    {
      id: 1,
      browser_name: 'Work Desktop',
      browser_uuid: 'EAGLE-RIVER-MOUNTAIN-42',
      last_seen: '2024-01-15T10:30:00Z',
      is_active: true,
      registered_at: '2024-01-10T10:00:00Z'
    },
    {
      id: 2,
      browser_name: 'Home Laptop',
      browser_uuid: 'TIGER-CLOUD-JADE-88',
      last_seen: '2024-01-14T15:20:00Z',
      is_active: true,
      registered_at: '2024-01-12T14:00:00Z'
    }
  ];

  beforeEach(async () => {
    mockBrowserService = jasmine.createSpyObj('RegisteredBrowserService', [
      'getAllBrowsers',
      'registerBrowser',
      'deleteBrowser',
      'verifyBrowser',
      'recoverBrowser'
    ]);
    mockBrowserUuidService = jasmine.createSpyObj('BrowserUuidService', [
      'getBrowserUuid',
      'getBrowserName',
      'generateFingerprint',
      'setBrowserUuid',
      'clearBrowserUuid'
    ]);
    mockSnackBar = jasmine.createSpyObj('MatSnackBar', ['open']);
    mockErrorDialog = jasmine.createSpyObj('ErrorDialogComponent', ['openErrorDialog']);

    await TestBed.configureTestingModule({
      imports: [
        RegisteredBrowserManagementComponent,
        ReactiveFormsModule,
        MatTableModule,
        MatCardModule,
        MatButtonModule,
        MatCheckboxModule,
        MatIconModule,
        MatFormFieldModule,
        MatInputModule,
        MatDialogModule,
        MatChipsModule,
        MatTooltipModule,
        MatProgressSpinnerModule,
        MatTabsModule,
        BrowserAnimationsModule
      ]
    })
    .overrideComponent(RegisteredBrowserManagementComponent, {
      set: {
        providers: [
          { provide: RegisteredBrowserService, useValue: mockBrowserService },
          { provide: BrowserUuidService, useValue: mockBrowserUuidService },
          { provide: MatSnackBar, useValue: mockSnackBar },
          { provide: ErrorDialogComponent, useValue: mockErrorDialog }
        ]
      }
    })
    .compileComponents();

    mockBrowserService.getAllBrowsers.and.returnValue(of(mockBrowsers));
    mockBrowserUuidService.getBrowserUuid.and.returnValue('EAGLE-RIVER-MOUNTAIN-42');
    mockBrowserUuidService.getBrowserName.and.returnValue('Chrome on Windows');
    mockBrowserUuidService.generateFingerprint.and.returnValue(Promise.resolve('fingerprint123'));
    mockBrowserService.verifyBrowser.and.returnValue(of({
      browser_uuid: 'EAGLE-RIVER-MOUNTAIN-42',
      browser_name: 'Work Desktop',
      verified: true
    }));

    fixture = TestBed.createComponent(RegisteredBrowserManagementComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should load devices on initialization', async () => {
      fixture.detectChanges();
      await fixture.whenStable();

      expect(mockBrowserService.getAllBrowsers).toHaveBeenCalled();
      expect(component.browsers).toEqual(mockBrowsers);
      expect(component.isLoading).toBe(false);
    });

    it('should verify current browser on initialization', async () => {
      fixture.detectChanges();
      await fixture.whenStable();

      expect(mockBrowserUuidService.getBrowserUuid).toHaveBeenCalled();
      expect(component.currentBrowserUuid).toBe('EAGLE-RIVER-MOUNTAIN-42');
    });

    it('should handle error when loading devices', async () => {
      const error = { error: { detail: 'Server error' } };
      mockBrowserService.getAllBrowsers.and.returnValue(throwError(() => error));

      fixture.detectChanges();
      await fixture.whenStable();

      expect(mockErrorDialog.openErrorDialog).toHaveBeenCalledWith('Failed to load devices', error);
      expect(component.isLoading).toBe(false);
    });
  });

  describe('generateBrowserUUID', () => {
    beforeEach(() => {
      fixture.detectChanges();
    });

    it('should generate UUID in correct format', () => {
      component.generateBrowserUUID();

      const uuid = component.registerForm.get('browser_uuid')?.value;

      // Verify format: WORD-WORD-WORD-NN
      const uuidPattern = /^[A-Z]+-[A-Z]+-[A-Z]+-\d{2}$/;
      expect(uuid).toMatch(uuidPattern);
    });

    it('should generate UUID with 4 segments separated by hyphens', () => {
      component.generateBrowserUUID();

      const uuid = component.registerForm.get('browser_uuid')?.value;
      const segments = uuid.split('-');

      expect(segments.length).toBe(4);
    });

    it('should generate UUID with 3 uppercase words', () => {
      component.generateBrowserUUID();

      const uuid = component.registerForm.get('browser_uuid')?.value;
      const segments = uuid.split('-');

      // First 3 segments should be uppercase words
      for (let i = 0; i < 3; i++) {
        expect(segments[i]).toMatch(/^[A-Z]+$/);
        expect(segments[i].length).toBeGreaterThan(0);
      }
    });

    it('should generate UUID with 2-digit number as last segment', () => {
      component.generateBrowserUUID();

      const uuid = component.registerForm.get('browser_uuid')?.value;
      const segments = uuid.split('-');
      const number = parseInt(segments[3]);

      expect(segments[3]).toMatch(/^\d{2}$/);
      expect(number).toBeGreaterThanOrEqual(10);
      expect(number).toBeLessThanOrEqual(99);
    });

    it('should update form with generated UUID', () => {
      const initialValue = component.registerForm.get('browser_uuid')?.value;
      expect(initialValue).toBe('');

      component.generateBrowserUUID();

      const newValue = component.registerForm.get('browser_uuid')?.value;
      expect(newValue).not.toBe('');
      expect(newValue).toMatch(/^[A-Z]+-[A-Z]+-[A-Z]+-\d{2}$/);
    });

    it('should generate different UUIDs on consecutive calls', () => {
      component.generateBrowserUUID();
      const uuid1 = component.registerForm.get('browser_uuid')?.value;

      component.generateBrowserUUID();
      const uuid2 = component.registerForm.get('browser_uuid')?.value;

      component.generateBrowserUUID();
      const uuid3 = component.registerForm.get('browser_uuid')?.value;

      // While theoretically possible to get duplicates, it's extremely unlikely
      // with proper randomization
      const allSame = uuid1 === uuid2 && uuid2 === uuid3;
      expect(allSame).toBe(false);
    });

    it('should use words from predefined word list', () => {
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

      component.generateBrowserUUID();

      const uuid = component.registerForm.get('browser_uuid')?.value;
      const words = uuid.split('-').slice(0, 3);

      // Each word should be from the word list
      words.forEach((word: string) => {
        expect(wordList).toContain(word);
      });
    });

    it('should generate human-readable UUIDs', () => {
      // Generate multiple UUIDs to verify they're all human-readable
      for (let i = 0; i < 10; i++) {
        component.generateBrowserUUID();
        const uuid = component.registerForm.get('browser_uuid')?.value;

        // Should have meaningful words, not random characters
        const segments = uuid.split('-');
        segments.slice(0, 3).forEach((word: string) => {
          // Words should be 3-7 characters (typical word length)
          expect(word.length).toBeGreaterThanOrEqual(3);
          expect(word.length).toBeLessThanOrEqual(7);
          // Should be all uppercase letters
          expect(word).toMatch(/^[A-Z]+$/);
        });
      }
    });
  });

  describe('Device Registration Form', () => {
    beforeEach(() => {
      fixture.detectChanges();
    });

    it('should initialize form with empty values', () => {
      expect(component.registerForm.get('browser_name')?.value).toBe('');
      expect(component.registerForm.get('browser_uuid')?.value).toBe('');
    });

    it('should validate browser name length', () => {
      const nameControl = component.registerForm.get('browser_name');

      // Too short
      nameControl?.setValue('ab');
      expect(nameControl?.hasError('minlength')).toBe(true);

      // Valid length
      nameControl?.setValue('My Device');
      expect(nameControl?.valid).toBe(true);
    });

    it('should require both browser name and UUID', () => {
      const form = component.registerForm;

      expect(form.valid).toBe(false);

      form.patchValue({
        browser_name: 'My Device',
        browser_uuid: ''
      });
      expect(form.valid).toBe(false);

      form.patchValue({
        browser_name: '',
        browser_uuid: 'EAGLE-RIVER-MOUNTAIN-42'
      });
      expect(form.valid).toBe(false);

      form.patchValue({
        browser_name: 'My Device',
        browser_uuid: 'EAGLE-RIVER-MOUNTAIN-42'
      });
      expect(form.valid).toBe(true);
    });
  });

  describe('registerBrowser', () => {
    beforeEach(() => {
      fixture.detectChanges();
    });

    it('should register browser with valid form data', fakeAsync(() => {
      const newBrowser: RegisteredBrowser = {
        id: 3,
        browser_name: 'Test Device',
        browser_uuid: 'EAGLE-RIVER-MOUNTAIN-42',
        last_seen: '2024-01-16T10:00:00Z',
        is_active: true,
        registered_at: '2024-01-16T10:00:00Z'
      };

      mockBrowserService.registerBrowser.and.returnValue(of(newBrowser));
      mockBrowserService.getAllBrowsers.and.returnValue(of([...mockBrowsers, newBrowser]));

      component.registerForm.patchValue({
        browser_name: 'Test Device',
        browser_uuid: 'EAGLE-RIVER-MOUNTAIN-42'
      });

      component.registerBrowser();
      tick(); // Process promise resolution and observable subscriptions

      expect(mockBrowserService.registerBrowser).toHaveBeenCalledWith(jasmine.objectContaining({
        browser_uuid: 'EAGLE-RIVER-MOUNTAIN-42',
        browser_name: 'Test Device',
        fingerprint_hash: 'fingerprint123',
        user_agent: navigator.userAgent
      }));
      expect(mockSnackBar.open).toHaveBeenCalledWith(
        'Device registered successfully',
        'Close',
        jasmine.objectContaining({ duration: 4000, panelClass: ['snack-success'] })
      );
    }));

    it('should not register with invalid form', async () => {
      component.registerForm.patchValue({
        browser_name: 'ab', // Too short
        browser_uuid: ''
      });

      await component.registerBrowser();

      expect(mockBrowserService.registerBrowser).not.toHaveBeenCalled();
    });

    it('should handle registration error', async () => {
      const error = { error: { detail: 'Device already exists' } };

      component.registerForm.patchValue({
        browser_name: 'Test Device',
        browser_uuid: 'EAGLE-RIVER-MOUNTAIN-42'
      });

      mockBrowserService.registerBrowser.and.returnValue(throwError(() => error));

      await component.registerBrowser();

      expect(mockErrorDialog.openErrorDialog).toHaveBeenCalledWith('Failed to register device', error);
      expect(component.isRegistering).toBe(false);
    });
  });

  describe('deleteBrowser', () => {
    beforeEach(() => {
      fixture.detectChanges();
    });

    it('should delete device after confirmation', fakeAsync(() => {
      spyOn(window, 'confirm').and.returnValue(true);

      mockBrowserService.deleteBrowser.and.returnValue(of(undefined));
      mockBrowserService.getAllBrowsers.and.returnValue(of(mockBrowsers.slice(1)));

      component.deleteBrowser(mockBrowsers[0]);
      tick();

      expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to revoke "Work Desktop"?');
      expect(mockBrowserService.deleteBrowser).toHaveBeenCalledWith(1);
      expect(mockSnackBar.open).toHaveBeenCalledWith(
        'Browser revoked successfully',
        'Close',
        jasmine.objectContaining({ duration: 4000, panelClass: ['snack-success'] })
      );
    }));

    it('should not delete if user cancels confirmation', () => {
      spyOn(window, 'confirm').and.returnValue(false);

      component.deleteBrowser(mockBrowsers[0]);

      expect(window.confirm).toHaveBeenCalled();
      expect(mockBrowserService.deleteBrowser).not.toHaveBeenCalled();
    });

    it('should handle deletion error', () => {
      const error = { error: { detail: 'Failed to delete' } };

      spyOn(window, 'confirm').and.returnValue(true);
      mockBrowserService.deleteBrowser.and.returnValue(throwError(() => error));

      component.deleteBrowser(mockBrowsers[0]);

      expect(mockErrorDialog.openErrorDialog).toHaveBeenCalledWith('Failed to revoke browser', error);
    });
  });
});
