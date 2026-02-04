import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { UpdateService, ReleaseInfo, UpdateStatus } from './update.service';

describe('UpdateService', () => {
  let service: UpdateService;
  let httpMock: HttpTestingController;
  const baseUrl = '/updater';

  const mockRelease: ReleaseInfo = {
    version: '1.1.0',
    tag_name: 'v1.1.0',
    published_at: '2026-01-15T00:00:00Z',
    release_notes: 'Bug fixes',
    download_url: 'https://github.com/dl/TAP-1.1.0.zip',
    asset_name: 'TAP-1.1.0.zip',
    asset_size: 50000000,
  };

  const mockStatus: UpdateStatus = {
    current_version: '1.0.0',
    latest_version: '1.1.0',
    update_available: true,
    last_checked: '2026-01-15T00:00:00Z',
    download_progress: null,
    downloaded_file: null,
    state: 'idle',
    error: null,
    backup_available: false,
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [UpdateService]
    });
    service = TestBed.inject(UpdateService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('checkForUpdate', () => {
    it('should call GET /updater/check', (done) => {
      service.checkForUpdate().subscribe(release => {
        expect(release).toEqual(mockRelease);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/check`);
      expect(req.request.method).toBe('GET');
      req.flush(mockRelease);
    });

    it('should set updateAvailable to true on success', (done) => {
      service.checkForUpdate().subscribe(() => {
        service.updateAvailable$.subscribe(available => {
          expect(available).toBe(true);
          done();
        });
      });

      const req = httpMock.expectOne(`${baseUrl}/check`);
      req.flush(mockRelease);
    });
  });

  describe('getStatus', () => {
    it('should call GET /updater/status', (done) => {
      service.getStatus().subscribe(status => {
        expect(status).toEqual(mockStatus);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/status`);
      expect(req.request.method).toBe('GET');
      req.flush(mockStatus);
    });

    it('should update updateAvailable$ from status', (done) => {
      service.getStatus().subscribe(() => {
        service.updateAvailable$.subscribe(available => {
          expect(available).toBe(true);
          done();
        });
      });

      const req = httpMock.expectOne(`${baseUrl}/status`);
      req.flush(mockStatus);
    });
  });

  describe('downloadUpdate', () => {
    it('should call POST /updater/download', (done) => {
      const mockResponse = { status: 'downloaded', file: '/path/to.zip', version: '1.1.0' };
      service.downloadUpdate().subscribe(result => {
        expect(result).toEqual(mockResponse);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/download`);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
    });
  });

  describe('applyUpdate', () => {
    it('should call POST /updater/apply', (done) => {
      const mockResponse = { status: 'applying', message: 'Server will restart' };
      service.applyUpdate().subscribe(result => {
        expect(result).toEqual(mockResponse);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/apply`);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
    });
  });

  describe('rollbackUpdate', () => {
    it('should call POST /updater/rollback', (done) => {
      const mockResponse = { status: 'rolling_back', message: 'Server will restart' };
      service.rollbackUpdate().subscribe(result => {
        expect(result).toEqual(mockResponse);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/rollback`);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
    });
  });

  describe('clearUpdateAvailable', () => {
    it('should set updateAvailable to false', (done) => {
      service.clearUpdateAvailable();
      service.updateAvailable$.subscribe(available => {
        expect(available).toBe(false);
        done();
      });
    });
  });
});
