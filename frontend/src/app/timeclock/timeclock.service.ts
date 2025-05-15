import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ClockResponse, TimeclockEntry } from './timeclock.interfaces';

/**
 * Service for managing timeclock entries
 * @class TimeclockService
 */
@Injectable({ providedIn: 'root' })
export class TimeclockService {
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

  /**
   * Get timeclock entries within a date range
   * @param start_date Optional start date of the range, first day of the month by default
   * @param end_date Optional end date of the range, today by default
   * @param employee_id Optional employee ID to filter by
   * @returns An array of timeclock entries
   */
  get_timeclock_entries(
    start_date?: Date,
    end_date?: Date,
    employee_id?: number
  ): Observable<TimeclockEntry[]> {
    if (!start_date) {
      start_date = new Date();
      start_date.setDate(1);
    }
    if (!end_date) {
      end_date = new Date();
    }

    let params = new HttpParams();
    params = params.set('start_date', start_date.toUTCString());
    params = params.set('end_date', end_date.toUTCString());
    if (employee_id) {
      params = params.set('employee_id', employee_id);
    }

    return this.http.get<TimeclockEntry[]>(`${this.base_url}`, {
      params,
    });
  }

  /**
   * Update a timeclock entry by ID
   * @param id The ID of the timeclock entry
   * @returns The updated timeclock entry
   */
  update_timeclock_entry(
    id: number,
    update: TimeclockEntry
  ): Observable<TimeclockEntry> {
    return this.http.post<TimeclockEntry>(`${this.base_url}/${id}`, update);
  }

  /**
   * Delete a timeclock entry by ID
   * @param id The ID of the timeclock entry
   * @returns void
   */
  delete_timeclock_entry(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base_url}/${id}`);
  }

  constructor() {}
}
