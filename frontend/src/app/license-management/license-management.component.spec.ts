import { ComponentFixture, TestBed, fakeAsync, tick, flush } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

import { LicenseManagementComponent } from './license-management.component';
import { LicenseService, LicenseStatus } from '../../services/license.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

describe('LicenseManagementComponent', () => {
  let component: LicenseManagementComponent;
  let fixture: ComponentFixture<LicenseManagementComponent>;
  let mockLicenseService: jasmine.SpyObj<LicenseService>;
  let mockSnackBar: jasmine.SpyObj<MatSnackBar>;
  let mockErrorDialog: jasmine.SpyObj<ErrorDialogComponent>;

  const mockActiveLicenseStatus: LicenseStatus = {
    is_active: true,
    license_key: 'EAGLE-RIVER-MOUNTAIN-42-TIGER-CLOUD-JADE-88',
    activated_at: '2024-01-15T10:30:00Z',
    server_id: 'server-123'
  };

  const mockInactiveLicenseStatus: LicenseStatus = {
    is_active: false,
    license_key: null,
    activated_at: null,
    server_id: null
  };

  beforeEach(async () => {
    mockLicenseService = jasmine.createSpyObj('LicenseService', [
      'getLicenseStatus',
      'activateLicense',
      'deactivateLicense'
    ]);
    mockSnackBar = jasmine.createSpyObj('MatSnackBar', ['open']);
    const mockSnackBarRef = jasmine.createSpyObj('MatSnackBarRef', ['dismiss', 'afterDismissed']);
    mockSnackBar.open.and.returnValue(mockSnackBarRef);
    mockErrorDialog = jasmine.createSpyObj('ErrorDialogComponent', ['openErrorDialog']);

    await TestBed.configureTestingModule({
      imports: [
        LicenseManagementComponent,
        ReactiveFormsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        BrowserAnimationsModule
      ]
    })
    .overrideComponent(LicenseManagementComponent, {
      set: {
        providers: [
          { provide: LicenseService, useValue: mockLicenseService },
          { provide: MatSnackBar, useValue: mockSnackBar },
          { provide: ErrorDialogComponent, useValue: mockErrorDialog }
        ]
      }
    })
    .compileComponents();

    fixture = TestBed.createComponent(LicenseManagementComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should load license status on initialization', () => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockInactiveLicenseStatus));

      fixture.detectChanges(); // Triggers ngOnInit

      expect(mockLicenseService.getLicenseStatus).toHaveBeenCalled();
      expect(component.licenseStatus).toEqual(mockInactiveLicenseStatus);
      expect(component.isLoading).toBe(false);
    });

    it('should handle error when loading license status', () => {
      const error = { error: { detail: 'Server error' } };
      mockLicenseService.getLicenseStatus.and.returnValue(throwError(() => error));

      fixture.detectChanges();

      expect(mockErrorDialog.openErrorDialog).toHaveBeenCalledWith('Failed to load license status', error);
      expect(component.isLoading).toBe(false);
    });
  });

  describe('License Form', () => {
    beforeEach(() => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockInactiveLicenseStatus));
      fixture.detectChanges();
    });

    it('should initialize form with empty values', () => {
      expect(component.licenseForm.get('license_key')?.value).toBe('');
    });

    it('should validate license key format', () => {
      const licenseKeyControl = component.licenseForm.get('license_key');

      // Valid format (128-char hex string)
      licenseKeyControl?.setValue('a'.repeat(128));
      expect(licenseKeyControl?.valid).toBe(true);

      // Invalid format - too short
      licenseKeyControl?.setValue('a'.repeat(64));
      expect(licenseKeyControl?.hasError('minlength')).toBe(true);

      // Invalid format - not hex
      licenseKeyControl?.setValue('z'.repeat(128));
      expect(licenseKeyControl?.hasError('pattern')).toBe(true);

      // Empty value
      licenseKeyControl?.setValue('');
      expect(licenseKeyControl?.hasError('required')).toBe(true);
    });

    it('should disable submit button when form is invalid', () => {
      const compiled = fixture.nativeElement;
      const submitButton = compiled.querySelector('button[type="submit"]');

      expect(submitButton.disabled).toBe(true);

      // Fill form with valid data (128-char hex string)
      component.licenseForm.patchValue({
        license_key: 'a'.repeat(128)
      });
      fixture.detectChanges();

      expect(submitButton.disabled).toBe(false);
    });
  });

  describe('activateLicense', () => {
    beforeEach(() => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockInactiveLicenseStatus));
      fixture.detectChanges();
    });

    it('should activate license with valid form data', (done) => {
      const licenseKey = 'a'.repeat(128); // 128-char hex string

      mockLicenseService.activateLicense.and.returnValue(of({
        id: 1,
        license_key: licenseKey,
        activated_at: '2024-01-15T10:30:00Z',
        is_active: true,
        server_id: 'server-123'
      }));
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockActiveLicenseStatus));

      component.licenseForm.setValue({
        license_key: licenseKey
      });

      // Verify the component has the mock snackBar
      const injectedSnackBar = TestBed.inject(MatSnackBar);
      console.log('Injected snackBar === mock?', injectedSnackBar === mockSnackBar);
      console.log('Component snackBar:', (component as any).snackBar);

      component.activateLicense();

      // Give Angular time to process the subscription
      setTimeout(() => {
        expect(mockLicenseService.activateLicense).toHaveBeenCalledWith(
          licenseKey
        );

        // Log all spy calls to debug
        console.log('errorDialog calls:', mockErrorDialog.openErrorDialog.calls.count());
        console.log('snackBar calls:', mockSnackBar.open.calls.count());
        console.log('getLicenseStatus calls:', mockLicenseService.getLicenseStatus.calls.count());

        expect(mockSnackBar.open).toHaveBeenCalledWith(
          'License activated successfully',
          'Close',
          jasmine.objectContaining({ duration: 4000, panelClass: ['snack-success'] })
        );
        expect(component.licenseForm.value.license_key).toBe(null);
        expect(component.isActivating).toBe(false);
        done();
      }, 100);
    });

    it('should not activate with invalid form', () => {
      component.licenseForm.patchValue({
        license_key: 'INVALID'
      });

      component.activateLicense();

      expect(mockLicenseService.activateLicense).not.toHaveBeenCalled();
    });

    it('should handle activation error', () => {
      const error = { error: { detail: 'Invalid license key' } };

      component.licenseForm.patchValue({
        license_key: 'a'.repeat(128)
      });

      mockLicenseService.activateLicense.and.returnValue(throwError(() => error));

      component.activateLicense();

      expect(mockErrorDialog.openErrorDialog).toHaveBeenCalledWith('Failed to activate license', error);
      expect(component.isActivating).toBe(false);
    });

    it('should set isActivating flag during activation', fakeAsync(() => {
      const licenseKey = 'a'.repeat(128);

      mockLicenseService.activateLicense.and.returnValue(of({
        id: 1,
        license_key: licenseKey,
        activated_at: '2024-01-15T10:30:00Z',
        is_active: true,
        server_id: 'server-123'
      }));
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockActiveLicenseStatus));

      component.licenseForm.patchValue({
        license_key: licenseKey
      });

      expect(component.isActivating).toBe(false);

      component.activateLicense();
      tick();

      expect(component.isActivating).toBe(false);
    }));
  });

  describe('deactivateLicense', () => {
    beforeEach(() => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockActiveLicenseStatus));
      fixture.detectChanges();
    });

    it('should deactivate license after confirmation', fakeAsync(() => {
      spyOn(window, 'confirm').and.returnValue(true);

      mockLicenseService.deactivateLicense.and.returnValue(of(undefined as any));
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockInactiveLicenseStatus));

      component.deactivateLicense();
      tick();

      expect(window.confirm).toHaveBeenCalledWith(
        'Are you sure you want to deactivate the current license? This will lock all admin features.'
      );
      expect(mockLicenseService.deactivateLicense).toHaveBeenCalled();
      expect(mockSnackBar.open).toHaveBeenCalledWith(
        'License deactivated',
        'Close',
        jasmine.objectContaining({ duration: 4000, panelClass: ['snack-success'] })
      );
      expect(component.isActivating).toBe(false);
    }));

    it('should not deactivate if user cancels confirmation', () => {
      spyOn(window, 'confirm').and.returnValue(false);

      component.deactivateLicense();

      expect(window.confirm).toHaveBeenCalled();
      expect(mockLicenseService.deactivateLicense).not.toHaveBeenCalled();
    });

    it('should handle deactivation error', () => {
      const error = { error: { detail: 'Failed to deactivate' } };

      spyOn(window, 'confirm').and.returnValue(true);
      mockLicenseService.deactivateLicense.and.returnValue(throwError(() => error));

      component.deactivateLicense();

      expect(mockErrorDialog.openErrorDialog).toHaveBeenCalledWith('Failed to deactivate license', error);
      expect(component.isActivating).toBe(false);
    });
  });

  describe('Template rendering', () => {
    it('should show loading spinner when isLoading is true', () => {
      // Set up mock to never resolve so isLoading stays true
      mockLicenseService.getLicenseStatus.and.returnValue(new Observable(() => {}));

      // Now detect changes - ngOnInit will be called and isLoading will be set to true
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const spinner = compiled.querySelector('mat-spinner');
      const loadingText = compiled.querySelector('.loading-container p');

      expect(component.isLoading).toBe(true);
      expect(spinner).toBeTruthy();
      expect(loadingText?.textContent?.trim()).toContain('Loading license status...');
    });

    it('should display active license status', () => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockActiveLicenseStatus));
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const statusTitle = compiled.querySelector('.status-active h3');
      const licenseKeyText = compiled.querySelector('.status-active p');

      expect(statusTitle?.textContent).toContain('License Active');
      expect(licenseKeyText?.textContent).toContain(mockActiveLicenseStatus.license_key);
    });

    it('should display inactive license status', () => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockInactiveLicenseStatus));
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const statusTitle = compiled.querySelector('.status-inactive h3');
      const statusMessage = compiled.querySelector('.status-inactive p');

      expect(statusTitle?.textContent).toContain('No Active License');
      expect(statusMessage?.textContent).toContain('Admin features are currently locked');
    });

    it('should show activation form when license is inactive', () => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockInactiveLicenseStatus));
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const activationCard = compiled.querySelector('.activation-card');
      const licenseKeyInput = compiled.querySelector('textarea[formControlName="license_key"]');

      expect(activationCard).toBeTruthy();
      expect(licenseKeyInput).toBeTruthy();
    });

    it('should not show activation form when license is active', () => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockActiveLicenseStatus));
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const activationCard = compiled.querySelector('.activation-card');

      expect(activationCard).toBeFalsy();
    });

    it('should show deactivate button when license is active', () => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockActiveLicenseStatus));
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const deactivateButton = compiled.querySelector('button[color="warn"]');

      expect(deactivateButton).toBeTruthy();
      expect(deactivateButton?.textContent).toContain('Deactivate License');
    });

    it('should always show help card', () => {
      mockLicenseService.getLicenseStatus.and.returnValue(of(mockInactiveLicenseStatus));
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const helpCard = compiled.querySelector('.help-card');

      expect(helpCard).toBeTruthy();
    });
  });
});
