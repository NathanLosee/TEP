import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ReportService, ReportRequest, ReportResponse } from './report.service';

describe('ReportService', () => {
  let service: ReportService;
  let httpMock: HttpTestingController;
  const baseUrl = '/reports';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ReportService]
    });
    service = TestBed.inject(ReportService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('generateReport', () => {
    it('should generate report for all employees', () => {
      const request: ReportRequest = {
        start_date: '2024-01-01',
        end_date: '2024-01-31'
      };

      const mockResponse: ReportResponse = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        report_type: 'employee',
        generated_at: '2024-01-31T12:00:00',
        employees: [
          {
            employee_id: 1,
            badge_number: '123',
            first_name: 'John',
            last_name: 'Doe',
            summary: {
              total_hours: 40.0,
              regular_hours: 40.0,
              overtime_hours: 0.0,
              holiday_hours: 0.0,
              days_worked: 5
            },
            months: []
          }
        ]
      };

      service.generateReport(request).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.employees.length).toBe(1);
        expect(response.employees[0].summary.total_hours).toBe(40.0);
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(request);
      req.flush(mockResponse);
    });

    it('should generate report for single employee', () => {
      const request: ReportRequest = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        employee_id: 1
      };

      const mockResponse: ReportResponse = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        report_type: 'employee',
        generated_at: '2024-01-31T12:00:00',
        employees: [
          {
            employee_id: 1,
            badge_number: '123',
            first_name: 'John',
            last_name: 'Doe',
            summary: {
              total_hours: 45.0,
              regular_hours: 40.0,
              overtime_hours: 5.0,
              holiday_hours: 0.0,
              days_worked: 6
            },
            months: []
          }
        ]
      };

      service.generateReport(request).subscribe(response => {
        expect(response.report_type).toBe('employee');
        expect(response.employees.length).toBe(1);
        expect(response.employees[0].employee_id).toBe(1);
        expect(response.employees[0].summary.overtime_hours).toBe(5.0);
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('POST');
      expect(req.request.body.employee_id).toBe(1);
      req.flush(mockResponse);
    });

    it('should generate report for department', () => {
      const request: ReportRequest = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        department_id: 5
      };

      const mockResponse: ReportResponse = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        report_type: 'department',
        generated_at: '2024-01-31T12:00:00',
        employees: []
      };

      service.generateReport(request).subscribe(response => {
        expect(response.report_type).toBe('department');
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.body.department_id).toBe(5);
      req.flush(mockResponse);
    });

    it('should generate report for org unit', () => {
      const request: ReportRequest = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        org_unit_id: 3
      };

      const mockResponse: ReportResponse = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        report_type: 'org_unit',
        generated_at: '2024-01-31T12:00:00',
        employees: []
      };

      service.generateReport(request).subscribe(response => {
        expect(response.report_type).toBe('org_unit');
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.body.org_unit_id).toBe(3);
      req.flush(mockResponse);
    });

    it('should handle HTTP error', () => {
      const request: ReportRequest = {
        start_date: '2024-01-01',
        end_date: '2024-01-31'
      };

      service.generateReport(request).subscribe({
        next: () => fail('should have failed with 403 error'),
        error: (error) => {
          expect(error.status).toBe(403);
          expect(error.error).toBe('Forbidden');
        }
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush('Forbidden', { status: 403, statusText: 'Forbidden' });
    });
  });

  describe('exportPDF', () => {
    it('should export PDF with summary detail level', () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      service.exportPDF('2024-01-01', '2024-01-31', 'summary').subscribe(blob => {
        expect(blob).toEqual(mockBlob);
        expect(blob.type).toBe('application/pdf');
      });

      const req = httpMock.expectOne(request =>
        request.url === `${baseUrl}/pdf` &&
        request.params.get('start_date') === '2024-01-01' &&
        request.params.get('end_date') === '2024-01-31' &&
        request.params.get('detail_level') === 'summary'
      );
      expect(req.request.method).toBe('GET');
      expect(req.request.responseType).toBe('blob');
      req.flush(mockBlob);
    });

    it('should export PDF with employee_summary detail level', () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      service.exportPDF('2024-01-01', '2024-01-31', 'employee_summary').subscribe(blob => {
        expect(blob).toBeTruthy();
      });

      const req = httpMock.expectOne(request =>
        request.params.get('detail_level') === 'employee_summary'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockBlob);
    });

    it('should export PDF with detailed level', () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      service.exportPDF('2024-01-01', '2024-01-31', 'detailed').subscribe(blob => {
        expect(blob).toBeTruthy();
      });

      const req = httpMock.expectOne(request =>
        request.params.get('detail_level') === 'detailed'
      );
      req.flush(mockBlob);
    });

    it('should export PDF with employee filter', () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      service.exportPDF('2024-01-01', '2024-01-31', 'detailed', 1).subscribe(blob => {
        expect(blob).toBeTruthy();
      });

      const req = httpMock.expectOne(request =>
        request.params.get('employee_id') === '1'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockBlob);
    });

    it('should export PDF with department filter', () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      service.exportPDF('2024-01-01', '2024-01-31', 'summary', undefined, 5).subscribe(blob => {
        expect(blob).toBeTruthy();
      });

      const req = httpMock.expectOne(request =>
        request.params.get('department_id') === '5'
      );
      req.flush(mockBlob);
    });

    it('should export PDF with org unit filter', () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      service.exportPDF('2024-01-01', '2024-01-31', 'summary', undefined, undefined, 3).subscribe(blob => {
        expect(blob).toBeTruthy();
      });

      const req = httpMock.expectOne(request =>
        request.params.get('org_unit_id') === '3'
      );
      req.flush(mockBlob);
    });

    it('should export PDF with all filters', () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      service.exportPDF('2024-01-01', '2024-01-31', 'detailed', 1, 5, 3).subscribe(blob => {
        expect(blob).toBeTruthy();
      });

      const req = httpMock.expectOne(request =>
        request.params.get('employee_id') === '1' &&
        request.params.get('department_id') === '5' &&
        request.params.get('org_unit_id') === '3'
      );
      req.flush(mockBlob);
    });

    it('should use default detail level when not specified', () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      service.exportPDF('2024-01-01', '2024-01-31').subscribe(blob => {
        expect(blob).toBeTruthy();
      });

      const req = httpMock.expectOne(request =>
        request.params.get('detail_level') === 'summary'
      );
      req.flush(mockBlob);
    });

    it('should handle PDF export error', () => {
      service.exportPDF('2024-01-01', '2024-01-31').subscribe({
        next: () => fail('should have failed with 500 error'),
        error: (error) => {
          expect(error.status).toBe(500);
        }
      });

      const req = httpMock.expectOne(request => request.url === `${baseUrl}/pdf`);
      req.error(new ProgressEvent('error'), { status: 500, statusText: 'Internal Server Error' });
    });
  });
});
