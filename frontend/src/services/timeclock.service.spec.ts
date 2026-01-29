import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TimeclockService, Timeclock, TimeclockEntry } from './timeclock.service';

describe('TimeclockService', () => {
  let service: TimeclockService;
  let httpMock: HttpTestingController;
  const baseUrl = '/timeclock';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [TimeclockService]
    });
    service = TestBed.inject(TimeclockService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('timeclock', () => {
    it('should clock in employee', () => {
      const badgeNumber = '123';
      const mockResponse: Timeclock = {
        status: 'success',
        message: 'Clocked in'
      };

      service.timeclock(badgeNumber).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.message).toBe('Clocked in');
      });

      const req = httpMock.expectOne(`${baseUrl}/${badgeNumber}`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toBeNull();
      req.flush(mockResponse);
    });

    it('should clock out employee', () => {
      const badgeNumber = '456';
      const mockResponse: Timeclock = {
        status: 'success',
        message: 'Clocked out'
      };

      service.timeclock(badgeNumber).subscribe(response => {
        expect(response.message).toBe('Clocked out');
      });

      const req = httpMock.expectOne(`${baseUrl}/${badgeNumber}`);
      req.flush(mockResponse);
    });

    it('should handle clock in/out error', () => {
      const badgeNumber = '999';

      service.timeclock(badgeNumber).subscribe({
        next: () => fail('should have failed with 404 error'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/${badgeNumber}`);
      req.flush('Employee not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('checkStatus', () => {
    it('should check clocked in status', () => {
      const badgeNumber = '123';
      const mockResponse: Timeclock = {
        status: 'success',
        message: 'Clocked in'
      };

      service.checkStatus(badgeNumber).subscribe(response => {
        expect(response.message).toBe('Clocked in');
      });

      const req = httpMock.expectOne(`${baseUrl}/${badgeNumber}/status`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should check clocked out status', () => {
      const badgeNumber = '456';
      const mockResponse: Timeclock = {
        status: 'success',
        message: 'Clocked out'
      };

      service.checkStatus(badgeNumber).subscribe(response => {
        expect(response.message).toBe('Clocked out');
      });

      const req = httpMock.expectOne(`${baseUrl}/${badgeNumber}/status`);
      req.flush(mockResponse);
    });

    it('should handle status check error', () => {
      const badgeNumber = '999';

      service.checkStatus(badgeNumber).subscribe({
        next: () => fail('should have failed with 403 error'),
        error: (error) => {
          expect(error.status).toBe(403);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/${badgeNumber}/status`);
      req.flush('Not authorized', { status: 403, statusText: 'Forbidden' });
    });
  });

  describe('getTimeclockEntries', () => {
    it('should get entries with default date range', () => {
      const mockEntries: TimeclockEntry[] = [
        {
          id: 1,
          badge_number: '123',
          first_name: 'John',
          last_name: 'Doe',
          clock_in: '2024-01-15T09:00:00',
          clock_out: '2024-01-15T17:00:00'
        }
      ];

      service.getTimeclockEntries().subscribe(entries => {
        expect(entries).toEqual(mockEntries);
        expect(entries.length).toBe(1);
      });

      const req = httpMock.expectOne(request =>
        request.url === baseUrl &&
        request.params.has('start_timestamp') &&
        request.params.has('end_timestamp')
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockEntries);
    });

    it('should get entries with custom date range', () => {
      const startDate = new Date('2024-01-01');
      const endDate = new Date('2024-01-31');
      const mockEntries: TimeclockEntry[] = [];

      service.getTimeclockEntries(startDate, endDate).subscribe(entries => {
        expect(entries).toEqual(mockEntries);
      });

      const req = httpMock.expectOne(request =>
        request.params.get('start_timestamp') === startDate.toISOString() &&
        request.params.get('end_timestamp') === endDate.toISOString()
      );
      req.flush(mockEntries);
    });

    it('should filter by badge number', () => {
      const badgeNumber = '123';
      const mockEntries: TimeclockEntry[] = [
        {
          id: 1,
          badge_number: badgeNumber,
          first_name: 'John',
          last_name: 'Doe',
          clock_in: '2024-01-15T09:00:00',
          clock_out: '2024-01-15T17:00:00'
        }
      ];

      service.getTimeclockEntries(undefined, undefined, badgeNumber).subscribe(entries => {
        expect(entries.length).toBe(1);
        expect(entries[0].badge_number).toBe(badgeNumber);
      });

      const req = httpMock.expectOne(request =>
        request.params.get('badge_number') === badgeNumber
      );
      req.flush(mockEntries);
    });

    it('should filter by first name', () => {
      const firstName = 'John';
      const mockEntries: TimeclockEntry[] = [
        {
          id: 1,
          badge_number: '123',
          first_name: firstName,
          last_name: 'Doe',
          clock_in: '2024-01-15T09:00:00',
          clock_out: '2024-01-15T17:00:00'
        }
      ];

      service.getTimeclockEntries(undefined, undefined, undefined, firstName).subscribe(entries => {
        expect(entries[0].first_name).toBe(firstName);
      });

      const req = httpMock.expectOne(request =>
        request.params.get('first_name') === firstName
      );
      req.flush(mockEntries);
    });

    it('should filter by last name', () => {
      const lastName = 'Doe';
      const mockEntries: TimeclockEntry[] = [];

      service.getTimeclockEntries(undefined, undefined, undefined, undefined, lastName).subscribe(entries => {
        expect(entries).toEqual(mockEntries);
      });

      const req = httpMock.expectOne(request =>
        request.params.get('last_name') === lastName
      );
      req.flush(mockEntries);
    });

    it('should filter by all parameters', () => {
      const startDate = new Date('2024-01-01');
      const endDate = new Date('2024-01-31');
      const badgeNumber = '123';
      const firstName = 'John';
      const lastName = 'Doe';
      const mockEntries: TimeclockEntry[] = [];

      service.getTimeclockEntries(startDate, endDate, badgeNumber, firstName, lastName).subscribe(entries => {
        expect(entries).toEqual(mockEntries);
      });

      const req = httpMock.expectOne(request =>
        request.params.get('badge_number') === badgeNumber &&
        request.params.get('first_name') === firstName &&
        request.params.get('last_name') === lastName
      );
      req.flush(mockEntries);
    });
  });

  describe('getEmployeeHistory', () => {
    it('should get employee history', () => {
      const badgeNumber = '123';
      const startDate = new Date('2024-01-01');
      const endDate = new Date('2024-01-31');
      const mockEntries: TimeclockEntry[] = [
        {
          id: 1,
          badge_number: badgeNumber,
          first_name: 'John',
          last_name: 'Doe',
          clock_in: '2024-01-15T09:00:00',
          clock_out: '2024-01-15T17:00:00'
        },
        {
          id: 2,
          badge_number: badgeNumber,
          first_name: 'John',
          last_name: 'Doe',
          clock_in: '2024-01-16T09:00:00',
          clock_out: '2024-01-16T17:00:00'
        }
      ];

      service.getEmployeeHistory(badgeNumber, startDate, endDate).subscribe(entries => {
        expect(entries.length).toBe(2);
        expect(entries[0].badge_number).toBe(badgeNumber);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${baseUrl}/${badgeNumber}/history` &&
        request.params.get('start_timestamp') === startDate.toISOString() &&
        request.params.get('end_timestamp') === endDate.toISOString()
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockEntries);
    });
  });

  describe('updateTimeclockEntry', () => {
    it('should update timeclock entry', () => {
      const entryId = 1;
      const update: TimeclockEntry = {
        id: entryId,
        badge_number: '123',
        first_name: 'John',
        last_name: 'Doe',
        clock_in: '2024-01-15T09:00:00',
        clock_out: '2024-01-15T18:00:00'
      };

      service.updateTimeclockEntry(entryId, update).subscribe(entry => {
        expect(entry).toEqual(update);
        expect(entry.clock_out).toBe('2024-01-15T18:00:00');
      });

      const req = httpMock.expectOne(`${baseUrl}/${entryId}`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(update);
      req.flush(update);
    });

    it('should handle update error', () => {
      const entryId = 999;
      const update: TimeclockEntry = {
        badge_number: '123',
        first_name: 'John',
        last_name: 'Doe',
        clock_in: '2024-01-15T09:00:00'
      };

      service.updateTimeclockEntry(entryId, update).subscribe({
        next: () => fail('should have failed with 404 error'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/${entryId}`);
      req.flush('Entry not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('deleteTimeclockEntry', () => {
    it('should delete timeclock entry', () => {
      const entryId = 1;

      service.deleteTimeclockEntry(entryId).subscribe(response => {
        expect(response).toBeNull();
      });

      const req = httpMock.expectOne(`${baseUrl}/${entryId}`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle delete error', () => {
      const entryId = 999;

      service.deleteTimeclockEntry(entryId).subscribe({
        next: () => fail('should have failed with 404 error'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/${entryId}`);
      req.flush('Entry not found', { status: 404, statusText: 'Not Found' });
    });
  });
});
