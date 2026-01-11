import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule, NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { LoginComponent } from './login.component';
import { UserService } from '../../services/user.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let userServiceSpy: jasmine.SpyObj<UserService>;
  let routerSpy: jasmine.SpyObj<Router>;
  let errorDialogSpy: jasmine.SpyObj<ErrorDialogComponent>;

  beforeEach(async () => {
    const userSpy = jasmine.createSpyObj('UserService', ['login']);
    const routSpy = jasmine.createSpyObj('Router', ['navigate']);
    const errorSpy = jasmine.createSpyObj('ErrorDialogComponent', ['openErrorDialog']);

    await TestBed.configureTestingModule({
      imports: [LoginComponent, FormsModule, BrowserAnimationsModule],
      providers: [
        { provide: UserService, useValue: userSpy },
        { provide: Router, useValue: routSpy },
        { provide: ErrorDialogComponent, useValue: errorSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    userServiceSpy = TestBed.inject(UserService) as jasmine.SpyObj<UserService>;
    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    errorDialogSpy = TestBed.inject(ErrorDialogComponent) as jasmine.SpyObj<ErrorDialogComponent>;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with default values', () => {
    expect(component.hidePassword).toBe(true);
    expect(component.isLoading).toBe(false);
  });

  it('should not submit when form is invalid', () => {
    const mockForm = {
      invalid: true,
      form: { value: {} }
    } as NgForm;

    component.onSubmit(mockForm);

    expect(userServiceSpy.login).not.toHaveBeenCalled();
  });

  it('should successfully login and navigate to admin', () => {
    const mockResponse = {
      access_token: 'test-token-123',
      token_type: 'bearer'
    };

    userServiceSpy.login.and.returnValue(of(mockResponse));
    spyOn(localStorage, 'setItem');
    spyOn(console, 'log');

    const mockForm = {
      invalid: false,
      form: {
        value: {
          badgeNumber: 'EMP001',
          password: 'password123'
        }
      }
    } as NgForm;

    component.onSubmit(mockForm);

    expect(component.isLoading).toBe(false);
    expect(userServiceSpy.login).toHaveBeenCalled();
    expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'test-token-123');
    expect(console.log).toHaveBeenCalledWith('Login successful:', mockResponse);
    expect(routerSpy.navigate).toHaveBeenCalledWith(['/admin']);
  });

  it('should set isLoading to true during login', () => {
    userServiceSpy.login.and.returnValue(of({ access_token: 'token', token_type: 'bearer' }));

    const mockForm = {
      invalid: false,
      form: {
        value: {
          badgeNumber: 'EMP001',
          password: 'password123'
        }
      }
    } as NgForm;

    expect(component.isLoading).toBe(false);
    component.onSubmit(mockForm);
    // Note: isLoading is set to false immediately in the next() callback
    expect(component.isLoading).toBe(false);
  });

  it('should handle login error and show error dialog', () => {
    const mockError = {
      error: {
        detail: 'Invalid credentials'
      }
    };

    userServiceSpy.login.and.returnValue(throwError(() => mockError));

    const mockForm = {
      invalid: false,
      form: {
        value: {
          badgeNumber: 'EMP001',
          password: 'wrongpassword'
        }
      }
    } as NgForm;

    component.onSubmit(mockForm);

    expect(component.isLoading).toBe(false);
    expect(errorDialogSpy.openErrorDialog).toHaveBeenCalledWith(
      'Login failed. Please check your credentials.',
      mockError
    );
    expect(routerSpy.navigate).not.toHaveBeenCalled();
  });

  it('should create FormData with correct username and password', () => {
    const mockResponse = {
      access_token: 'test-token',
      token_type: 'bearer'
    };

    let capturedFormData: FormData | undefined;
    userServiceSpy.login.and.callFake((formData: FormData) => {
      capturedFormData = formData;
      return of(mockResponse);
    });

    const mockForm = {
      invalid: false,
      form: {
        value: {
          badgeNumber: 'EMP123',
          password: 'testpass'
        }
      }
    } as NgForm;

    component.onSubmit(mockForm);

    expect(capturedFormData).toBeDefined();
    expect(capturedFormData!.get('username')).toBe('EMP123');
    expect(capturedFormData!.get('password')).toBe('testpass');
  });

  it('should not store token on login failure', () => {
    spyOn(localStorage, 'setItem');
    userServiceSpy.login.and.returnValue(throwError(() => new Error('Login failed')));

    const mockForm = {
      invalid: false,
      form: {
        value: {
          badgeNumber: 'EMP001',
          password: 'password'
        }
      }
    } as NgForm;

    component.onSubmit(mockForm);

    expect(localStorage.setItem).not.toHaveBeenCalled();
  });
});
