import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ClockResponse } from './clocker.interfaces';

/**
 * Service for handling clocking in and out of employees
 * @class ClockerService
 */
@Injectable({ providedIn: 'root' })
export class ClockerService {
  private http = inject(HttpClient);
  base_url = 'http://localhost:8080/timeclock';

  /**
   * Clock in/out for an employee
   * @param employee_id The employee ID to clock in/out
   * @returns Whether the ID was clocked in or out
   */
  timeclock(employee_id: number): Observable<ClockResponse> {
    return this.http.post<ClockResponse>(`${this.base_url}`, null, {
      params: { employee_id: employee_id },
    });
  }

  constructor() {}
}
