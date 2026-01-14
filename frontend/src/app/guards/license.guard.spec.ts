import { TestBed } from '@angular/core/testing';
import { Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { licenseGuard } from './license.guard';
import { LicenseService } from '../../services/license.service';

describe('licenseGuard', () => {
  let mockLicenseService: jasmine.SpyObj<LicenseService>;
  let mockRouter: jasmine.SpyObj<Router>;
  let mockRoute: ActivatedRouteSnapshot;
  let mockState: RouterStateSnapshot;

  beforeEach(() => {
    mockLicenseService = jasmine.createSpyObj('LicenseService', ['isLicensed']);
    mockRouter = jasmine.createSpyObj('Router', ['navigate']);
    mockRoute = {} as ActivatedRouteSnapshot;
    mockState = { url: '/admin/users' } as RouterStateSnapshot;

    TestBed.configureTestingModule({
      providers: [
        { provide: LicenseService, useValue: mockLicenseService },
        { provide: Router, useValue: mockRouter }
      ]
    });
  });

  it('should allow navigation when license is active', () => {
    mockLicenseService.isLicensed.and.returnValue(true);

    const result = TestBed.runInInjectionContext(() => licenseGuard(mockRoute, mockState));

    expect(result).toBe(true);
    expect(mockRouter.navigate).not.toHaveBeenCalled();
  });

  it('should block navigation and redirect when license is inactive', () => {
    mockLicenseService.isLicensed.and.returnValue(false);

    const result = TestBed.runInInjectionContext(() => licenseGuard(mockRoute, mockState));

    expect(result).toBe(false);
    expect(mockRouter.navigate).toHaveBeenCalledWith(['/admin/license']);
  });

  it('should check license status using LicenseService', () => {
    mockLicenseService.isLicensed.and.returnValue(true);

    TestBed.runInInjectionContext(() => licenseGuard(mockRoute, mockState));

    expect(mockLicenseService.isLicensed).toHaveBeenCalled();
  });

  describe('Integration with routing', () => {
    it('should protect admin routes from unlicensed access', () => {
      // Simulate unlicensed state
      mockLicenseService.isLicensed.and.returnValue(false);

      const result = TestBed.runInInjectionContext(() => licenseGuard(mockRoute, mockState));

      expect(result).toBe(false);
      expect(mockRouter.navigate).toHaveBeenCalledWith(['/admin/license']);
    });

    it('should allow access to admin routes with valid license', () => {
      // Simulate licensed state
      mockLicenseService.isLicensed.and.returnValue(true);

      const result = TestBed.runInInjectionContext(() => licenseGuard(mockRoute, mockState));

      expect(result).toBe(true);
      expect(mockRouter.navigate).not.toHaveBeenCalled();
    });
  });

  describe('Multiple guard evaluations', () => {
    it('should consistently check license status on each evaluation', () => {
      // First call - unlicensed
      mockLicenseService.isLicensed.and.returnValue(false);
      let result = TestBed.runInInjectionContext(() => licenseGuard(mockRoute, mockState));
      expect(result).toBe(false);
      expect(mockLicenseService.isLicensed).toHaveBeenCalledTimes(1);

      // Second call - licensed
      mockLicenseService.isLicensed.and.returnValue(true);
      result = TestBed.runInInjectionContext(() => licenseGuard(mockRoute, mockState));
      expect(result).toBe(true);
      expect(mockLicenseService.isLicensed).toHaveBeenCalledTimes(2);

      // Third call - unlicensed again
      mockLicenseService.isLicensed.and.returnValue(false);
      result = TestBed.runInInjectionContext(() => licenseGuard(mockRoute, mockState));
      expect(result).toBe(false);
      expect(mockLicenseService.isLicensed).toHaveBeenCalledTimes(3);
    });
  });
});
