import { TestBed } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { ErrorDialogComponent, ErrorDialog } from './error-dialog.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

describe('ErrorDialogComponent', () => {
  let service: ErrorDialogComponent;
  let dialogSpy: jasmine.SpyObj<MatDialog>;

  beforeEach(() => {
    const spy = jasmine.createSpyObj('MatDialog', ['open']);

    TestBed.configureTestingModule({
      imports: [BrowserAnimationsModule],
      providers: [
        ErrorDialogComponent,
        { provide: MatDialog, useValue: spy }
      ]
    });

    service = TestBed.inject(ErrorDialogComponent);
    dialogSpy = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should open dialog with string error', () => {
    const errorMessage = 'Test error message';
    const errorString = 'Detailed error information';

    service.openErrorDialog(errorMessage, errorString);

    expect(dialogSpy.open).toHaveBeenCalledWith(ErrorDialog, {
      height: '300px',
      width: '300px',
      enterAnimationDuration: 250,
      exitAnimationDuration: 1000,
      data: {
        errorMessage: errorString
      },
      panelClass: 'error-dialog'
    });
  });

  it('should open dialog with error object', () => {
    const errorMessage = 'Test error message';
    const errorObject = {
      error: {
        detail: 'API error detail'
      }
    };

    service.openErrorDialog(errorMessage, errorObject);

    expect(dialogSpy.open).toHaveBeenCalledWith(ErrorDialog, {
      height: '300px',
      width: '300px',
      enterAnimationDuration: 250,
      exitAnimationDuration: 1000,
      data: {
        errorMessage: 'API error detail'
      },
      panelClass: 'error-dialog'
    });
  });

  it('should open error dialog without logging to console', () => {
    spyOn(console, 'error');
    const errorMessage = 'Test error';
    const error = 'Error details';

    service.openErrorDialog(errorMessage, error);

    expect(console.error).not.toHaveBeenCalled();
  });
});

// ErrorDialog is a simple component that only injects MAT_DIALOG_DATA
// Testing it in isolation doesn't provide value as it's just a presentation component
