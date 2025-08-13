import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Timeclock {
  status: string;
  message: string;
}

export interface TimeclockEntry {
  id?: number;
  clockIn: Date;
  clockOut: Date;
  badgeNumber: string;
  firstName: string;
  lastName: string;
}

/**
 * Service for handling clocking in and out of employees
 * @class ClockerService
 */
@Injectable({ providedIn: 'root' })
export class TimeclockService {
  private http = inject(HttpClient);
  baseUrl = 'timeclock';

  /**
   * Clock in/out for an employee
   * @param employee_id The employee ID to clock in/out
   * @returns Whether the ID was clocked in or out
   */
  timeclock(badgeNumber: string): Observable<Timeclock> {
    return this.http.post<Timeclock>(`${this.baseUrl}/${badgeNumber}`, null);
  }

  /**
   * Check the status of an employee (clocked in or out)
   * @param employee_id The employee ID to check the status of
   * @returns The status of the employee (clocked in or out)
   */
  checkStatus(badgeNumber: string): Observable<Timeclock> {
    return this.http.get<Timeclock>(`${this.baseUrl}/${badgeNumber}/status`);
  }

  /**
   * Get timeclock entries within a date range
   * @param startDate Optional start date of the range, first day of the month by default
   * @param endDate Optional end date of the range, today by default
   * @param badgeNumber Optional badge number to filter by
   * @param firstName Optional first name to filter by
   * @param lastName Optional last name to filter by
   * @returns An array of timeclock entries
   */
  getTimeclockEntries(
    startDate?: Date,
    endDate?: Date,
    badgeNumber?: string,
    firstName?: string,
    lastName?: string
  ): Observable<TimeclockEntry[]> {
    if (!startDate) {
      startDate = new Date();
      startDate.setDate(1);
    }
    if (!endDate) {
      endDate = new Date();
    }

    let params = new HttpParams();
    params = params.set('start_date', startDate.toUTCString());
    params = params.set('end_date', endDate.toUTCString());
    if (badgeNumber) {
      params = params.set('badge_number', badgeNumber);
    }
    if (firstName) {
      params = params.set('first_name', firstName);
    }
    if (lastName) {
      params = params.set('last_name', lastName);
    }

    return this.http.get<TimeclockEntry[]>(`${this.baseUrl}`, {
      params,
    });
  }

  /**
   * Update a timeclock entry by ID
   * @param id The ID of the timeclock entry
   * @returns The updated timeclock entry
   */
  updateTimeclockEntry(
    id: number,
    update: TimeclockEntry
  ): Observable<TimeclockEntry> {
    return this.http.post<TimeclockEntry>(`${this.baseUrl}/${id}`, update);
  }

  /**
   * Delete a timeclock entry by ID
   * @param id The ID of the timeclock entry
   * @returns void
   */
  deleteTimeclockEntry(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  constructor() {}
}
