import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface TimePeriod {
  id: number;
  clock_in: string;
  clock_out: string | null;
  hours: number;
}

export interface DayDetail {
  date: string;
  total_hours: number;
  periods: TimePeriod[];
}

export interface MonthDetail {
  month: number;
  year: number;
  total_hours: number;
  days: DayDetail[];
}

export interface EmployeeSummary {
  total_hours: number;
  regular_hours: number;
  overtime_hours: number;
  holiday_hours: number;
  days_worked: number;
}

export interface EmployeeReportData {
  employee_id: number;
  badge_number: string;
  first_name: string;
  last_name: string;
  summary: EmployeeSummary;
  months: MonthDetail[];
}

export interface ReportResponse {
  start_date: string;
  end_date: string;
  report_type: string;
  generated_at: string;
  employees: EmployeeReportData[];
}

export interface ReportRequest {
  start_date: string;
  end_date: string;
  employee_id?: number;
  department_id?: number;
  org_unit_id?: number;
  detail_level?: string;
}

/**
 * Service for handling report operations
 */
@Injectable({ providedIn: 'root' })
export class ReportService {
  private http = inject(HttpClient);
  private baseUrl = '/reports';

  /**
   * Generate a timeclock report
   */
  generateReport(request: ReportRequest): Observable<ReportResponse> {
    return this.http.post<ReportResponse>(this.baseUrl, request);
  }

  /**
   * Export report as PDF
   */
  exportPDF(
    startDate: string,
    endDate: string,
    detailLevel: 'summary' | 'employee_summary' | 'detailed' = 'summary',
    employeeId?: number,
    departmentId?: number,
    orgUnitId?: number
  ): Observable<Blob> {
    let params = new HttpParams()
      .set('start_date', startDate)
      .set('end_date', endDate)
      .set('detail_level', detailLevel);

    if (employeeId) {
      params = params.set('employee_id', employeeId.toString());
    }
    if (departmentId) {
      params = params.set('department_id', departmentId.toString());
    }
    if (orgUnitId) {
      params = params.set('org_unit_id', orgUnitId.toString());
    }

    return this.http.get(`${this.baseUrl}/pdf`, {
      params,
      responseType: 'blob',
    });
  }
}
