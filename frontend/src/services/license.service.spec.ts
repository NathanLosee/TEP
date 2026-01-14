import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { LicenseService, LicenseStatus, LicenseActivationResponse } from './license.service';
import { environment } from '../environments/environment';

describe('LicenseService', () => {
  let service: LicenseService;
  let httpMock: HttpTestingController;
  const baseUrl = '/licenses';

  const mockActiveLicenseStatus: LicenseStatus = {
    is_active: true,
    license_key: 'EAGLE-RIVER-MOUNTAIN-42-TIGER-CLOUD-JADE-88',
    activated_at: '2024-01-15T10:30:00Z',
    server_id: 'server-123'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [LicenseService]
    });
    service = TestBed.inject(LicenseService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('checkLicense', () => {
    it('should fetch license status and update BehaviorSubject on success', (done) => {
      const mockStatus: LicenseStatus = {
        is_active: true,
        license_key: 'EAGLE-RIVER-MOUNTAIN-42-TIGER-CLOUD-JADE-88',
        activated_at: '2024-01-15T10:30:00Z',
        server_id: 'server-123'
      };

      service.checkLicense();

      const req = httpMock.expectOne(`${baseUrl}/status`);
      expect(req.request.method).toBe('GET');
      req.flush(mockStatus);

      // Verify the BehaviorSubject was updated
      service['licenseStatus$'].subscribe(status => {
        expect(status).toEqual(mockStatus);
        done();
      });
    });

    it('should set inactive status on error', (done) => {
      service.checkLicense();

      const req = httpMock.expectOne(`${baseUrl}/status`);
      req.error(new ProgressEvent('error'));

      // Verify the BehaviorSubject was updated with inactive status
      service['licenseStatus$'].subscribe(status => {
        expect(status?.is_active).toBe(false);
        expect(status?.license_key).toBeNull();
        done();
      });
    });
  });

  describe('getLicenseStatus', () => {
    it('should return observable of license status', (done) => {
      const mockStatus: LicenseStatus = {
        is_active: true,
        license_key: 'EAGLE-RIVER-MOUNTAIN-42-TIGER-CLOUD-JADE-88',
        activated_at: '2024-01-15T10:30:00Z',
        server_id: 'server-123'
      };

      service.getLicenseStatus().subscribe(status => {
        expect(status).toEqual(mockStatus);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/status`);
      expect(req.request.method).toBe('GET');
      req.flush(mockStatus);
    });

    it('should handle error when fetching license status', (done) => {
      service.getLicenseStatus().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toBeTruthy();
          done();
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/status`);
      req.error(new ProgressEvent('error'));
    });
  });

  describe('activateLicense', () => {
    it('should send activation request and return response', (done) => {
      const licenseKey = 'a'.repeat(128); // 128-char hex signature (which IS the license key now)
      const mockResponse: LicenseActivationResponse = {
        id: 1,
        license_key: licenseKey,
        activated_at: '2024-01-15T10:30:00Z',
        is_active: true,
        server_id: 'server-123'
      };

      service.activateLicense(licenseKey).subscribe(response => {
        expect(response).toEqual(mockResponse);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/activate`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body.license_key).toEqual(licenseKey);

      // Handle the checkLicense call that happens after activation
      req.flush(mockResponse);

      const statusReq = httpMock.expectOne(`${baseUrl}/status`);
      statusReq.flush(mockActiveLicenseStatus);
    });

    it('should handle activation error', (done) => {
      const licenseKey = 'INVALID-KEY';

      service.activateLicense(licenseKey).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toBeTruthy();
          done();
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/activate`);
      req.flush({ detail: 'Invalid license key' }, { status: 400, statusText: 'Bad Request' });
    });

    it('should update license status after successful activation', (done) => {
      const licenseKey = 'a'.repeat(128); // 128-char hex signature
      const mockResponse: LicenseActivationResponse = {
        id: 1,
        license_key: licenseKey,
        activated_at: '2024-01-15T10:30:00Z',
        is_active: true,
        server_id: 'server-123'
      };

      service.activateLicense(licenseKey).subscribe(() => {
        // After activation, checkLicense is called
        const statusReq = httpMock.expectOne(`${baseUrl}/status`);
        statusReq.flush({
          is_active: true,
          license_key: licenseKey,
          activated_at: '2024-01-15T10:30:00Z',
          server_id: 'server-123'
        });

        service.isLicensed$().subscribe(isLicensed => {
          expect(isLicensed).toBe(true);
          done();
        });
      });

      const req = httpMock.expectOne(`${baseUrl}/activate`);
      req.flush(mockResponse);
    });
  });

  describe('deactivateLicense', () => {
    it('should send deactivation request', (done) => {
      service.deactivateLicense().subscribe(() => {
        expect(true).toBe(true); // Just verify it completes
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/deactivate`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle deactivation error', (done) => {
      service.deactivateLicense().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toBeTruthy();
          done();
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/deactivate`);
      req.flush({ detail: 'No active license found' }, { status: 404, statusText: 'Not Found' });
    });

    it('should update license status after successful deactivation', (done) => {
      service.deactivateLicense().subscribe(() => {
        service.isLicensed$().subscribe(isLicensed => {
          expect(isLicensed).toBe(false);
          done();
        });
      });

      const req = httpMock.expectOne(`${baseUrl}/deactivate`);
      req.flush(null);
    });
  });

  describe('isLicensed', () => {
    it('should return true when license is active', () => {
      const mockStatus: LicenseStatus = {
        is_active: true,
        license_key: 'EAGLE-RIVER-MOUNTAIN-42-TIGER-CLOUD-JADE-88',
        activated_at: '2024-01-15T10:30:00Z',
        server_id: 'server-123'
      };

      service['licenseStatus$'].next(mockStatus);
      expect(service.isLicensed()).toBe(true);
    });

    it('should return false when license is inactive', () => {
      const mockStatus: LicenseStatus = {
        is_active: false,
        license_key: null,
        activated_at: null,
        server_id: null
      };

      service['licenseStatus$'].next(mockStatus);
      expect(service.isLicensed()).toBe(false);
    });

    it('should return false when status is null', () => {
      service['licenseStatus$'].next(null);
      expect(service.isLicensed()).toBe(false);
    });
  });

  describe('isLicensed$', () => {
    it('should emit true when license is active', () => {
      const mockStatus: LicenseStatus = {
        is_active: true,
        license_key: 'EAGLE-RIVER-MOUNTAIN-42-TIGER-CLOUD-JADE-88',
        activated_at: '2024-01-15T10:30:00Z',
        server_id: 'server-123'
      };

      service['licenseStatus$'].next(mockStatus);

      let result: boolean | undefined;
      service.isLicensed$().subscribe(isLicensed => {
        result = isLicensed;
      });

      expect(result).toBe(true);
    });

    it('should emit false when license is inactive', () => {
      const mockStatus: LicenseStatus = {
        is_active: false,
        license_key: null,
        activated_at: null,
        server_id: null
      };

      service['licenseStatus$'].next(mockStatus);

      let result: boolean | undefined;
      service.isLicensed$().subscribe(isLicensed => {
        result = isLicensed;
      });

      expect(result).toBe(false);
    });

    it('should emit false when status is null', () => {
      service['licenseStatus$'].next(null);

      let result: boolean | undefined;
      service.isLicensed$().subscribe(isLicensed => {
        result = isLicensed;
      });

      expect(result).toBe(false);
    });

    it('should emit updates when license status changes', (done) => {
      const updates: boolean[] = [];

      const subscription = service.isLicensed$().subscribe(isLicensed => {
        updates.push(isLicensed);

        // Complete after receiving 3 updates
        if (updates.length === 3) {
          expect(updates[0]).toBe(false); // Initial null state
          expect(updates[1]).toBe(true);  // After activation
          expect(updates[2]).toBe(false); // After deactivation
          subscription.unsubscribe();
          done();
        }
      });

      // Activate license
      setTimeout(() => {
        service['licenseStatus$'].next({
          is_active: true,
          license_key: 'EAGLE-RIVER-MOUNTAIN-42-TIGER-CLOUD-JADE-88',
          activated_at: '2024-01-15T10:30:00Z',
          server_id: 'server-123'
        });
      }, 10);

      // Deactivate license
      setTimeout(() => {
        service['licenseStatus$'].next({
          is_active: false,
          license_key: null,
          activated_at: null,
          server_id: null
        });
      }, 20);
    });
  });
});
