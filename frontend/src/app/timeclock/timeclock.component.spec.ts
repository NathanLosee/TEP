import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { TimeclockComponent, TimeclockDialog } from './timeclock.component';
import { TimeclockService } from '../../services/timeclock.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

describe('TimeclockComponent', () => {
  let component: TimeclockComponent;
  let fixture: ComponentFixture<TimeclockComponent>;
  let timeclockServiceSpy: jasmine.SpyObj<TimeclockService>;
  let dialogSpy: jasmine.SpyObj<MatDialog>;
  let errorDialogSpy: jasmine.SpyObj<ErrorDialogComponent>;

  beforeEach(async () => {
    const timeclockSpy = jasmine.createSpyObj('TimeclockService', ['timeclock', 'checkStatus']);
    const matDialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    const errorSpy = jasmine.createSpyObj('ErrorDialogComponent', ['openErrorDialog']);

    await TestBed.configureTestingModule({
      imports: [TimeclockComponent, FormsModule, BrowserAnimationsModule],
      providers: [
        { provide: TimeclockService, useValue: timeclockSpy },
        { provide: MatDialog, useValue: matDialogSpy },
        { provide: ErrorDialogComponent, useValue: errorSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(TimeclockComponent);
    component = fixture.componentInstance;
    timeclockServiceSpy = TestBed.inject(TimeclockService) as jasmine.SpyObj<TimeclockService>;
    dialogSpy = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
    errorDialogSpy = TestBed.inject(ErrorDialogComponent) as jasmine.SpyObj<ErrorDialogComponent>;

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
      spyOn(console, 'log');
      spyOn(component, 'openTimeclockDialog').and.callThrough();

      component.badgeNumber = 'EMP001';
      component.clockInOut();

      expect(timeclockServiceSpy.timeclock).toHaveBeenCalledWith('EMP001');
      expect(console.log).toHaveBeenCalledWith(mockResponse);
      expect(component.openTimeclockDialog).toHaveBeenCalledWith('EMP001', 'Clocked in');
      expect(component.badgeNumber).toBe('');
    });

    it('should handle clock in/out error', () => {
      const mockError = {
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
      timeclockServiceSpy.timeclock.and.returnValue(throwError(() => new Error('Error')));
      component.badgeNumber = 'EMP001';

      component.clockInOut();

      expect(component.badgeNumber).toBe('EMP001');
    });
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
      spyOn(console, 'log');
      spyOn(component, 'openTimeclockDialog').and.callThrough();

      component.badgeNumber = 'EMP002';
      component.checkStatus();

      expect(timeclockServiceSpy.checkStatus).toHaveBeenCalledWith('EMP002');
      expect(console.log).toHaveBeenCalledWith(mockResponse);
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
