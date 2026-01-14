import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Employee } from './employee.service';

export interface Holiday {
  name: string;
  start_date: Date;
  end_date: Date;
  is_recurring?: boolean;
  recurrence_type?: 'fixed' | 'relative' | null;
  recurrence_month?: number | null;
  recurrence_day?: number | null;
  recurrence_week?: number | null;
  recurrence_weekday?: number | null;
}

export interface HolidayGroup {
  id?: number;
  name: string;
  holidays: Holiday[];
}

/**
 * Service for handling holiday group operations
 */
@Injectable({ providedIn: 'root' })
export class HolidayGroupService {
  private http = inject(HttpClient);
  private baseUrl = '/holiday_groups';

  /**
   * Create a new holiday group
   * @param holidayGroup The holiday group data to create
   * @returns The created holiday group
   */
  createHolidayGroup(holidayGroup: HolidayGroup): Observable<HolidayGroup> {
    return this.http.post<HolidayGroup>(`${this.baseUrl}`, holidayGroup);
  }

  /**
   * Get all holiday groups
   * @returns An array of holiday groups
   */
  getHolidayGroups(): Observable<HolidayGroup[]> {
    return this.http.get<HolidayGroup[]>(`${this.baseUrl}`);
  }

  /**
   * Get holiday group by ID
   * @param id The ID of the holiday group to retrieve
   * @returns The holiday group with the specified ID
   */
  getHolidayGroupById(id: number): Observable<HolidayGroup> {
    return this.http.get<HolidayGroup>(`${this.baseUrl}/${id}`);
  }

  /**
   * Get employees by holiday group
   * @param holidayGroupId The ID of the holiday group to retrieve employees from
   * @returns An array of employees in the specified holiday group
   */
  getEmployeesByHolidayGroup(holidayGroupId: number): Observable<Employee[]> {
    return this.http.get<Employee[]>(
      `${this.baseUrl}/${holidayGroupId}/employees`
    );
  }

  /**
   * Update an existing holiday group
   * @param id The ID of the holiday group to update
   * @param holidayGroup The updated holiday group data
   * @returns The updated holiday group
   */
  updateHolidayGroup(
    id: number,
    holidayGroup: HolidayGroup
  ): Observable<HolidayGroup> {
    return this.http.put<HolidayGroup>(`${this.baseUrl}/${id}`, holidayGroup);
  }

  /**
   * Delete a holiday group
   * @param id The ID of the holiday group to delete
   * @returns An observable indicating the completion of the delete operation
   */
  deleteHolidayGroup(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
