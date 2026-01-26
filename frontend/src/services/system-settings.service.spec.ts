import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { SystemSettingsService, SystemSettings, SystemSettingsUpdate } from './system-settings.service';

describe('SystemSettingsService', () => {
  let service: SystemSettingsService;
  let httpMock: HttpTestingController;
  const baseUrl = '/system-settings';

  const mockSettings: SystemSettings = {
    id: 1,
    primary_color: '#673AB7',
    secondary_color: '#FF4081',
    accent_color: '#FFD740',
    company_name: 'Test Company',
    has_logo: false,
    logo_filename: null
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [SystemSettingsService]
    });
    service = TestBed.inject(SystemSettingsService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getSettings', () => {
    it('should fetch settings and update BehaviorSubject', (done) => {
      service.getSettings().subscribe(settings => {
        expect(settings).toEqual(mockSettings);
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('GET');
      req.flush(mockSettings);
    });

    it('should handle error when fetching settings', (done) => {
      service.getSettings().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toBeTruthy();
          done();
        }
      });

      const req = httpMock.expectOne(baseUrl);
      req.error(new ProgressEvent('error'));
    });
  });

  describe('getSettings$', () => {
    it('should return observable of cached settings', (done) => {
      // First load settings
      service.getSettings().subscribe(() => {
        // Then check cached observable
        service.getSettings$().subscribe(settings => {
          expect(settings).toEqual(mockSettings);
          done();
        });
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush(mockSettings);
    });

    it('should emit null initially', (done) => {
      service.getSettings$().subscribe(settings => {
        expect(settings).toBeNull();
        done();
      });
    });
  });

  describe('getCachedSettings', () => {
    it('should return null initially', () => {
      expect(service.getCachedSettings()).toBeNull();
    });

    it('should return cached settings after fetch', (done) => {
      service.getSettings().subscribe(() => {
        expect(service.getCachedSettings()).toEqual(mockSettings);
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush(mockSettings);
    });
  });

  describe('updateSettings', () => {
    it('should send update request and update cached settings', (done) => {
      const update: SystemSettingsUpdate = {
        company_name: 'Updated Company',
        primary_color: '#123456'
      };

      const updatedSettings: SystemSettings = {
        ...mockSettings,
        company_name: 'Updated Company',
        primary_color: '#123456'
      };

      service.updateSettings(update).subscribe(settings => {
        expect(settings).toEqual(updatedSettings);
        expect(service.getCachedSettings()).toEqual(updatedSettings);
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(update);
      req.flush(updatedSettings);
    });

    it('should handle error when updating settings', (done) => {
      const update: SystemSettingsUpdate = { company_name: 'Test' };

      service.updateSettings(update).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toBeTruthy();
          done();
        }
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush({ detail: 'Error' }, { status: 400, statusText: 'Bad Request' });
    });
  });

  describe('uploadLogo', () => {
    it('should upload logo file and update cached settings', (done) => {
      const file = new File(['test'], 'logo.png', { type: 'image/png' });
      const settingsWithLogo: SystemSettings = {
        ...mockSettings,
        has_logo: true,
        logo_filename: 'logo.png'
      };

      service.uploadLogo(file).subscribe(settings => {
        expect(settings).toEqual(settingsWithLogo);
        expect(service.getCachedSettings()).toEqual(settingsWithLogo);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/logo`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body instanceof FormData).toBe(true);
      req.flush(settingsWithLogo);
    });

    it('should handle error when uploading logo', (done) => {
      const file = new File(['test'], 'logo.png', { type: 'image/png' });

      service.uploadLogo(file).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toBeTruthy();
          done();
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/logo`);
      req.flush({ detail: 'File too large' }, { status: 400, statusText: 'Bad Request' });
    });
  });

  describe('getLogoUrl', () => {
    it('should return correct logo URL', () => {
      expect(service.getLogoUrl()).toBe(`${baseUrl}/logo`);
    });
  });

  describe('deleteLogo', () => {
    it('should delete logo and update cached settings', (done) => {
      // First set up settings with logo
      const settingsWithLogo: SystemSettings = {
        ...mockSettings,
        has_logo: true,
        logo_filename: 'logo.png'
      };

      service.getSettings().subscribe(() => {
        service.deleteLogo().subscribe(() => {
          const cached = service.getCachedSettings();
          expect(cached?.has_logo).toBe(false);
          expect(cached?.logo_filename).toBeNull();
          done();
        });

        const deleteReq = httpMock.expectOne(`${baseUrl}/logo`);
        expect(deleteReq.request.method).toBe('DELETE');
        deleteReq.flush(null);
      });

      const getReq = httpMock.expectOne(baseUrl);
      getReq.flush(settingsWithLogo);
    });

    it('should handle error when deleting logo', (done) => {
      service.deleteLogo().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toBeTruthy();
          done();
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/logo`);
      req.flush({ detail: 'Error' }, { status: 500, statusText: 'Server Error' });
    });
  });

  describe('applyTheme', () => {
    it('should set CSS custom properties', () => {
      const root = document.documentElement;
      const originalStyle = root.style.getPropertyValue('--sys-primary');

      service.applyTheme(mockSettings);

      expect(root.style.getPropertyValue('--sys-primary')).toBe(mockSettings.primary_color);
      expect(root.style.getPropertyValue('--sys-secondary')).toBe(mockSettings.secondary_color);
      expect(root.style.getPropertyValue('--sys-tertiary')).toBe(mockSettings.accent_color);

      // Clean up
      root.style.setProperty('--sys-primary', originalStyle);
    });
  });

  describe('color utilities', () => {
    it('should correctly identify contrast colors', () => {
      // Light background should get dark text
      const lightSettings: SystemSettings = {
        ...mockSettings,
        primary_color: '#FFFFFF'
      };
      service.applyTheme(lightSettings);
      expect(document.documentElement.style.getPropertyValue('--sys-on-primary')).toBe('#000000');

      // Dark background should get light text
      const darkSettings: SystemSettings = {
        ...mockSettings,
        primary_color: '#000000'
      };
      service.applyTheme(darkSettings);
      expect(document.documentElement.style.getPropertyValue('--sys-on-primary')).toBe('#FFFFFF');
    });
  });
});
