import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of, throwError } from 'rxjs';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { UpdateManagementComponent } from './update-management.component';
import { UpdateService, UpdateStatus, ReleaseInfo } from '../../services/update.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

describe('UpdateManagementComponent', () => {
  let component: UpdateManagementComponent;
  let fixture: ComponentFixture<UpdateManagementComponent>;
  let updateServiceSpy: jasmine.SpyObj<UpdateService>;
  let mockErrorDialog: jasmine.SpyObj<ErrorDialogComponent>;

  const mockStatus: UpdateStatus = {
    current_version: '1.0.0',
    latest_version: null,
    update_available: false,
    last_checked: null,
    download_progress: null,
    downloaded_file: null,
    state: 'idle',
    error: null,
    backup_available: false,
  };

  const mockRelease: ReleaseInfo = {
    version: '1.1.0',
    tag_name: 'v1.1.0',
    published_at: '2026-01-15T00:00:00Z',
    release_notes: 'Bug fixes',
    download_url: 'https://github.com/dl/TAP-1.1.0.zip',
    asset_name: 'TAP-1.1.0.zip',
    asset_size: 50000000,
  };

  beforeEach(async () => {
    updateServiceSpy = jasmine.createSpyObj('UpdateService', [
      'checkForUpdate', 'getStatus', 'downloadUpdate', 'applyUpdate', 'rollbackUpdate'
    ], {
      updateAvailable$: new BehaviorSubject<boolean>(false),
      status$: new BehaviorSubject<UpdateStatus | null>(null),
    });
    updateServiceSpy.getStatus.and.returnValue(of(mockStatus));
    updateServiceSpy.checkForUpdate.and.returnValue(of(mockRelease));
    updateServiceSpy.downloadUpdate.and.returnValue(of({ status: 'downloaded', file: '/path', version: '1.1.0' }));
    updateServiceSpy.applyUpdate.and.returnValue(of({ status: 'applying', message: 'Restarting' }));
    updateServiceSpy.rollbackUpdate.and.returnValue(of({ status: 'rolling_back', message: 'Restarting' }));

    mockErrorDialog = jasmine.createSpyObj('ErrorDialogComponent', ['openErrorDialog']);

    await TestBed.configureTestingModule({
      imports: [UpdateManagementComponent, NoopAnimationsModule],
    })
      .overrideComponent(UpdateManagementComponent, {
        set: {
          providers: [
            { provide: UpdateService, useValue: updateServiceSpy },
            { provide: ErrorDialogComponent, useValue: mockErrorDialog },
          ],
        },
      })
      .compileComponents();

    fixture = TestBed.createComponent(UpdateManagementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load status on init', () => {
    expect(updateServiceSpy.getStatus).toHaveBeenCalled();
    expect(component.status).toEqual(mockStatus);
    expect(component.isLoading).toBeFalse();
  });

  it('should display current version', () => {
    const compiled = fixture.nativeElement;
    expect(compiled.textContent).toContain('v1.0.0');
  });

  it('should check for updates', () => {
    component.checkForUpdate();
    expect(updateServiceSpy.checkForUpdate).toHaveBeenCalled();
    expect(component.releaseInfo).toEqual(mockRelease);
  });

  it('should handle check with no update available', () => {
    updateServiceSpy.checkForUpdate.and.returnValue(
      throwError(() => ({ status: 204 }))
    );
    component.checkForUpdate();
    expect(component.isChecking).toBeFalse();
  });

  it('should handle download', () => {
    component.downloadUpdate();
    expect(updateServiceSpy.downloadUpdate).toHaveBeenCalled();
  });

  it('should format bytes correctly', () => {
    expect(component.formatBytes(0)).toBe('0 B');
    expect(component.formatBytes(1024)).toBe('1 KB');
    expect(component.formatBytes(1048576)).toBe('1 MB');
    expect(component.formatBytes(50000000)).toBe('47.7 MB');
  });

  it('should format date correctly', () => {
    expect(component.formatDate(null)).toBe('Never');
    expect(component.formatDate('2026-01-15T00:00:00Z')).toBeTruthy();
  });

  it('should show error card when state is error', () => {
    component.status = { ...mockStatus, state: 'error', error: 'Something failed' };
    fixture.detectChanges();
    const compiled = fixture.nativeElement;
    expect(compiled.textContent).toContain('Something failed');
  });
});
