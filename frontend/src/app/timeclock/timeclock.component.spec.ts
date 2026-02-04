import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BehaviorSubject, of, Subject, throwError } from 'rxjs';

import { TimeclockComponent, TimeclockDialog } from './timeclock.component';
import { TimeclockService } from '../../services/timeclock.service';
import { BrowserUuidService } from '../../services/browser-uuid.service';
import { RegisteredBrowserService } from '../../services/registered-browser.service';
import { OfflineQueueService } from '../../services/offline-queue.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

describe('TimeclockComponent', () => {
  let component: TimeclockComponent;
  let fixture: ComponentFixture<TimeclockComponent>;
  let timeclockServiceSpy: jasmine.SpyObj<TimeclockService>;
  let browserUuidServiceSpy: jasmine.SpyObj<BrowserUuidService>;
  let registeredBrowserServiceSpy: jasmine.SpyObj<RegisteredBrowserService>;
  let offlineQueueServiceSpy: jasmine.SpyObj<OfflineQueueService>;
  let dialogSpy: jasmine.SpyObj<MatDialog>;
  let errorDialogSpy: jasmine.SpyObj<ErrorDialogComponent>;
  let pendingCount$: BehaviorSubject<number>;
  let isOffline$: BehaviorSubject<boolean>;

  beforeEach(async () => {
    const timeclockSpy = jasmine.createSpyObj('TimeclockService', ['timeclock', 'checkStatus']);
    const browserUuidSpy = jasmine.createSpyObj('BrowserUuidService', [
      'getBrowserUuid',
      'getBrowserName',
      'generateFingerprint',
      'setBrowserUuid',
      'clearBrowserUuid'
    ]);
    const registeredBrowserSpy = jasmine.createSpyObj('RegisteredBrowserService', [
      'verifyBrowser',
      'getAllBrowsers',
      'registerBrowser',
      'deleteBrowser',
      'recoverBrowser'
    ]);

    pendingCount$ = new BehaviorSubject<number>(0);
    isOffline$ = new BehaviorSubject<boolean>(false);
    const offlineQueueSpy = jasmine.createSpyObj('OfflineQueueService', ['enqueue', 'syncAll'], {
      pendingCount$,
      isOffline$,
      lastSyncResult$: new Subject(),
    });
    offlineQueueSpy.enqueue.and.returnValue(Promise.resolve({ badgeNumber: '', clientTimestamp: '', status: 'pending' as const, attempts: 0, createdAt: '' }));

    const matDialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    const errorSpy = jasmine.createSpyObj('ErrorDialogComponent', ['openErrorDialog']);

    await TestBed.configureTestingModule({
      imports: [TimeclockComponent, FormsModule, BrowserAnimationsModule]
    })
    .overrideComponent(TimeclockComponent, {
      set: {
        providers: [
          { provide: TimeclockService, useValue: timeclockSpy },
          { provide: BrowserUuidService, useValue: browserUuidSpy },
          { provide: RegisteredBrowserService, useValue: registeredBrowserSpy },
          { provide: OfflineQueueService, useValue: offlineQueueSpy },
          { provide: MatDialog, useValue: matDialogSpy },
          { provide: ErrorDialogComponent, useValue: errorSpy }
        ]
      }
    })
    .compileComponents();

    timeclockServiceSpy = timeclockSpy;
    browserUuidServiceSpy = browserUuidSpy;
    registeredBrowserServiceSpy = registeredBrowserSpy;
    offlineQueueServiceSpy = offlineQueueSpy;
    dialogSpy = matDialogSpy;
    errorDialogSpy = errorSpy;

    // Set up default return values for browser services
    browserUuidServiceSpy.generateFingerprint.and.returnValue(Promise.resolve('test-fingerprint'));
    browserUuidServiceSpy.getBrowserUuid.and.returnValue('TEST-UUID-123');
    browserUuidServiceSpy.getBrowserName.and.returnValue('Test Browser');
    registeredBrowserServiceSpy.verifyBrowser.and.returnValue(of({
      verified: true,
      browser_uuid: 'TEST-UUID-123',
      browser_name: 'Test Browser',
      restored: false
    }));

    fixture = TestBed.createComponent(TimeclockComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  afterEach(() => {
    component.ngOnDestroy();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with empty badge number', () => {
    expect(component.badgeNumber).toBe('');
  });

  it('should initialize current date and time', () => {
    expect(component.currentDateAndTime).toBeDefined();
    expect(typeof component.currentDateAndTime).toBe('number');
  });

  it('should update current date and time every minute', fakeAsync(() => {
    const initialTime = component.currentDateAndTime;

    tick(60001); // Advance 1 minute + 1ms to ensure the timer fires

    expect(component.currentDateAndTime).toBeGreaterThanOrEqual(initialTime);
  }));

  it('should unsubscribe from clock on destroy', () => {
    const subscription = component['clockSubscription'];
    spyOn(subscription!, 'unsubscribe');

    component.ngOnDestroy();

    expect(subscription!.unsubscribe).toHaveBeenCalled();
  });

  describe('clockInOut', () => {
    it('should successfully clock in/out and open dialog', () => {
      const mockResponse = {
        status: 'success',
        message: 'Clocked in'
      };

      const mockDialogRef = {
        afterOpened: () => of(undefined),
        close: jasmine.createSpy('close')
      } as any;

      timeclockServiceSpy.timeclock.and.returnValue(of(mockResponse));
      dialogSpy.open.and.returnValue(mockDialogRef);
      spyOn(component, 'openTimeclockDialog').and.callThrough();

      component.badgeNumber = 'EMP001';
      component.clockInOut();

      expect(timeclockServiceSpy.timeclock).toHaveBeenCalledWith('EMP001');
      expect(component.openTimeclockDialog).toHaveBeenCalledWith('EMP001', 'Clocked in');
      expect(component.badgeNumber).toBe('');
    });

    it('should handle clock in/out error', () => {
      const mockError = {
        status: 404,
        error: {
          detail: 'Employee not found'
        }
      };

      timeclockServiceSpy.timeclock.and.returnValue(throwError(() => mockError));
      component.badgeNumber = 'INVALID';

      component.clockInOut();

      expect(errorDialogSpy.openErrorDialog).toHaveBeenCalledWith(
        'Failed to clock in/out',
        mockError
      );
    });

    it('should not clear badge number on error', () => {
      const mockError = { status: 400, error: { detail: 'Bad request' } };
      timeclockServiceSpy.timeclock.and.returnValue(throwError(() => mockError));
      component.badgeNumber = 'EMP001';

      component.clockInOut();

      expect(component.badgeNumber).toBe('EMP001');
    });

    it('should queue punch when offline', fakeAsync(() => {
      const mockDialogRef = {
        afterOpened: () => of(undefined),
        close: jasmine.createSpy('close')
      } as any;
      dialogSpy.open.and.returnValue(mockDialogRef);

      isOffline$.next(true);
      component.badgeNumber = 'EMP001';
      component.clockInOut();
      tick();

      expect(offlineQueueServiceSpy.enqueue).toHaveBeenCalledWith('EMP001');
      expect(component.badgeNumber).toBe('');
    }));

    it('should fall back to queue on network error', fakeAsync(() => {
      const mockDialogRef = {
        afterOpened: () => of(undefined),
        close: jasmine.createSpy('close')
      } as any;
      dialogSpy.open.and.returnValue(mockDialogRef);

      const networkError = { status: 0 };
      timeclockServiceSpy.timeclock.and.returnValue(throwError(() => networkError));
      component.badgeNumber = 'EMP001';
      component.clockInOut();
      tick();

      expect(offlineQueueServiceSpy.enqueue).toHaveBeenCalledWith('EMP001');
    }));
  });

  describe('checkStatus', () => {
    it('should successfully check status and open dialog', () => {
      const mockResponse = {
        status: 'success',
        message: 'Clocked out'
      };

      const mockDialogRef = {
        afterOpened: () => of(undefined),
        close: jasmine.createSpy('close')
      } as any;

      timeclockServiceSpy.checkStatus.and.returnValue(of(mockResponse));
      dialogSpy.open.and.returnValue(mockDialogRef);
      spyOn(component, 'openTimeclockDialog').and.callThrough();

      component.badgeNumber = 'EMP002';
      component.checkStatus();

      expect(timeclockServiceSpy.checkStatus).toHaveBeenCalledWith('EMP002');
      expect(component.openTimeclockDialog).toHaveBeenCalledWith('EMP002', 'Clocked out');
    });

    it('should handle check status error', () => {
      const mockError = {
        error: {
          detail: 'Not authorized'
        }
      };

      timeclockServiceSpy.checkStatus.and.returnValue(throwError(() => mockError));
      component.badgeNumber = 'EMP001';

      component.checkStatus();

      expect(errorDialogSpy.openErrorDialog).toHaveBeenCalledWith(
        'Failed to check status',
        mockError
      );
    });
  });

  describe('openTimeclockDialog', () => {
    it('should open dialog with correct data', () => {
      const mockDialogRef = {
        afterOpened: () => of(undefined),
        close: jasmine.createSpy('close')
      } as any;

      dialogSpy.open.and.returnValue(mockDialogRef);

      component.openTimeclockDialog('EMP123', 'Clocked in');

      expect(dialogSpy.open).toHaveBeenCalledWith(TimeclockDialog, {
        height: '300px',
        width: '300px',
        enterAnimationDuration: 500,
        exitAnimationDuration: 1000,
        data: {
          badgeNumber: 'EMP123',
          timeclockStatus: 'Clocked in'
        }
      });
    });

    it('should auto-close dialog after 3.5 seconds', fakeAsync(() => {
      const mockDialogRef = {
        afterOpened: () => of(undefined),
        close: jasmine.createSpy('close')
      } as any;

      dialogSpy.open.and.returnValue(mockDialogRef);

      component.openTimeclockDialog('EMP123', 'Clocked in');

      expect(mockDialogRef.close).not.toHaveBeenCalled();

      tick(3500);

      expect(mockDialogRef.close).toHaveBeenCalled();
    }));
  });
});

// TimeclockDialog is a simple component that only injects MAT_DIALOG_DATA
// Testing it in isolation doesn't provide value as it's just a presentation component
