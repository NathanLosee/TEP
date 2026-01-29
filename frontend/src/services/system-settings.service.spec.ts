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
        // Response should match server response
        expect(settings).toEqual(settingsWithLogo);

        // Cached settings should have the logo info plus logo_updated_at
        const cached = service.getCachedSettings();
        expect(cached?.has_logo).toBe(true);
        expect(cached?.logo_filename).toBe('logo.png');
        expect(cached?.logo_updated_at).toBeDefined();
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
    it('should return correct logo URL with cache buster', () => {
      const url = service.getLogoUrl();
      // URL should contain the base path and a cache buster param
      expect(url).toContain('/system-settings/logo');
      expect(url).toContain('?t=');
    });

    it('should use provided cache buster', () => {
      const url = service.getLogoUrl(12345);
      expect(url).toContain('?t=12345');
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
    afterEach(() => {
      // Clean up any custom theme
      service.clearCustomTheme();
    });

    it('should set CSS custom properties with tonal palette for non-default colors', () => {
      const root = document.documentElement;

      // Use non-default colors so they actually get applied
      const customSettings: SystemSettings = {
        ...mockSettings,
        primary_color: '#FF0000',  // Not the default #673AB7
        secondary_color: '#00FF00',  // Not the default #FF4081
        accent_color: '#0000FF'  // Not the default #FFD740
      };

      service.applyTheme(customSettings);

      // Check that theme properties are set (tonal palette values, not raw colors)
      expect(root.style.getPropertyValue('--sys-primary')).toBeTruthy();
      expect(root.style.getPropertyValue('--app-primary-base'))
        .toBe(customSettings.primary_color);
      expect(root.style.getPropertyValue('--app-secondary-base'))
        .toBe(customSettings.secondary_color);
      expect(root.style.getPropertyValue('--app-tertiary-base'))
        .toBe(customSettings.accent_color);
    });

    it('should clear custom theme for default colors', () => {
      const root = document.documentElement;

      // First apply custom colors
      const customSettings: SystemSettings = {
        ...mockSettings,
        primary_color: '#FF0000',
        secondary_color: '#00FF00',
        accent_color: '#0000FF'
      };
      service.applyTheme(customSettings);
      expect(root.style.getPropertyValue('--sys-primary')).toBeTruthy();

      // Then apply default colors - should clear
      // These are the actual default colors from SystemSettingsService
      const defaultSettings: SystemSettings = {
        ...mockSettings,
        primary_color: '#02E600',  // SystemSettingsService.DEFAULT_PRIMARY
        secondary_color: '#BBCBB2',  // SystemSettingsService.DEFAULT_SECONDARY
        accent_color: '#CDCD00'  // SystemSettingsService.DEFAULT_ACCENT
      };
      service.applyTheme(defaultSettings);

      // Should be cleared (empty string)
      expect(root.style.getPropertyValue('--sys-primary')).toBe('');
    });
  });

  describe('color utilities', () => {
    afterEach(() => {
      service.clearCustomTheme();
    });

    it('should set on-primary color from tonal palette', () => {
      // The service uses tone20 for --sys-on-primary, not direct luminance check
      const customSettings: SystemSettings = {
        ...mockSettings,
        primary_color: '#FF0000'  // Non-default color
      };
      service.applyTheme(customSettings);

      // on-primary should be set (tone20 of the palette)
      const onPrimary = document.documentElement.style.getPropertyValue(
        '--sys-on-primary'
      );
      expect(onPrimary).toBeTruthy();
    });
  });
});
